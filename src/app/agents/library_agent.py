from transformers import pipeline
from src.app.graph.state import ResearchState, Paper
from typing import List

# Use a simple text-generation model for summarization
summarizer = pipeline("text-generation", model="gpt2")

def save_papers(state: ResearchState) -> dict:
    selected_ids = state.get("selected_paper_ids", [])
    retrieved = state.get("retrieved_papers", [])
    existing = state.get("saved_papers", [])

    newly_saved = []
    for p in retrieved:
        if p["paper_id"] in selected_ids:
            try:
                prompt = f"Summarize this medical abstract in one sentence: {p['abstract'][:200]}"
                result = summarizer(prompt, max_new_tokens=50, do_sample=False)
                p["summary"] = result[0]["generated_text"].replace(prompt, "").strip()
            except Exception:
                p["summary"] = p["abstract"]
            newly_saved.append(p)

    existing_ids = {p["paper_id"] for p in existing}
    merged = existing + [p for p in newly_saved if p["paper_id"] not in existing_ids]
    return {"saved_papers": merged}

def get_library(state: ResearchState) -> List[Paper]:
    return state.get("saved_papers", [])