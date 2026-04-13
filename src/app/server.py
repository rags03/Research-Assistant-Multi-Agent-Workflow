import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from src.app.graph.edges import build_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

def get_session(session_id: str):
    if session_id not in sessions:
        graph = build_graph()
        config = {"configurable": {"thread_id": session_id}}
        initial_state = {
            "topic": None, "time_period": None, "study_type": None,
            "current_question": None, "current_field": None,
            "intake_complete": False, "retrieved_papers": None,
            "selected_paper_ids": None, "retrieval_complete": False,
            "saved_papers": [], "user_input": None, "stage": "intake"
        }
        state = graph.invoke(initial_state, config)
        sessions[session_id] = {"graph": graph, "config": config, "state": state}
    return sessions[session_id]

class UserInput(BaseModel):
    session_id: str
    message: str

class SelectPapers(BaseModel):
    session_id: str
    paper_ids: List[str]

class RemovePaper(BaseModel):
    session_id: str
    paper_id: str

@app.get("/")
def root():
    return FileResponse("src/app/index.html")

@app.get("/start")
def start(session_id: str = "default"):
    session = get_session(session_id)
    state = session["state"]
    return {
        "message": state.get("current_question"),
        "stage": state.get("stage")
    }

@app.post("/chat")
def chat(body: UserInput):
    session = get_session(body.session_id)
    graph = session["graph"]
    config = session["config"]

    graph.update_state(config, {"user_input": body.message})
    state = graph.invoke(None, config)
    session["state"] = state

    # If papers were retrieved, show them regardless of stage name
    if state.get("retrieved_papers"):
        return {
            "stage": "retrieval",
            "papers": state.get("retrieved_papers", []),
            "message": f"Found {len(state.get('retrieved_papers', []))} papers. Select the ones you want to save."
        }

    if state.get("intake_complete") and not state.get("retrieved_papers"):
        # Trigger retrieval
        state = graph.invoke(None, config)
        session["state"] = state
        return {
            "stage": "retrieval",
            "papers": state.get("retrieved_papers", []),
            "message": f"Found {len(state.get('retrieved_papers', []))} papers. Select the ones you want to save."
        }

    return {
        "message": state.get("current_question"),
        "stage": state.get("stage")
    }

@app.post("/select")
def select_papers(body: SelectPapers):
    session = get_session(body.session_id)
    graph = session["graph"]
    config = session["config"]

    graph.update_state(config, {"selected_paper_ids": body.paper_ids})
    state = graph.invoke(None, config)
    session["state"] = state

    return {
        "stage": "library",
        "saved_papers": state.get("saved_papers", []),
        "message": f"Saved {len(body.paper_ids)} papers to your library."
    }

@app.post("/restart")
def restart(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "Session restarted"}

@app.delete("/remove")
def remove_paper(body: RemovePaper):
    session = get_session(body.session_id)
    state = session["state"]
    saved = state.get("saved_papers", [])
    updated = [p for p in saved if p["paper_id"] != body.paper_id]
    session["state"]["saved_papers"] = updated
    graph = session["graph"]
    config = session["config"]
    graph.update_state(config, {"saved_papers": updated})
    return {"saved_papers": updated}

@app.get("/library")
def get_library(session_id: str = "default"):
    session = get_session(session_id)
    return {"saved_papers": session["state"].get("saved_papers", [])}