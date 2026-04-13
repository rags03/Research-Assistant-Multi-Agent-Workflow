# Medical Research Assistant — Multi-Agent Workflow

A multi-agent AI system that helps researchers discover, evaluate, and save medical/biology papers from arXiv. Built with LangGraph, HuggingFace, and Groq.

---

## What It Does

1. **Intake Agent** — Asks the user 3 structured questions to understand their research need (topic, time period, study type)
2. **Retrieval Agent** — Searches arXiv for relevant papers based on the user's profile, filtered by medical/biology categories
3. **Library Agent** — Uses a local HuggingFace model (GPT-2) to summarize selected papers and saves them to a personal library

---

## Architecture

```
User → Intake Agent (LangGraph) → Retrieval Agent (arXiv API) → Library Agent (HuggingFace GPT-2)
```

- **LangGraph** orchestrates the multi-agent conversation flow
- **arXiv API** fetches live research papers sorted by relevance
- **HuggingFace GPT-2** runs locally for paper summarization (no API key needed)
- **Groq LLaMA 3.1** powers RAGAS evaluation scoring
- **FastAPI** serves the backend
- **HTML/JS** provides the frontend with a split-panel UI

---

## Prerequisites

- Python 3.12
- A free Groq API key — sign up at https://console.groq.com

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/rags03/Research-Assistant-Multi-Agent-Workflow.git
cd Research-Assistant-Multi-Agent-Workflow
```

### 2. Create a virtual environment
```bash
py -3.12 -m venv venv
```

### 3. Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up your API key

Copy the example env file:
```bash
cp .env.example .env
```

Open `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
HF_HUB_DISABLE_SYMLINKS_WARNING=1
```

### 6. Run the application
```bash
uvicorn src.app.server:app
```

### 7. Open in your browser

Go to: **http://localhost:8000**

---

## How to Use

1. Answer the 3 intake questions about your research topic
2. Browse the retrieved papers and check the ones you want to save
3. Click **Save Selected Papers** to add them to your library
4. Click **🔄 New Search** to start a new query

---

## Project Structure

```
Research-Assistant-Multi-Agent-Workflow/
├── src/
│   └── app/
│       ├── agents/
│       │   ├── intake_agent.py       # Intake Agent — structured Q&A
│       │   ├── retrieval_agent.py    # Retrieval Agent — arXiv search
│       │   └── library_agent.py      # Library Agent — HuggingFace summarization
│       ├── graph/
│       │   ├── edges.py              # LangGraph graph definition
│       │   └── state.py              # Shared state schema
│       ├── rag/
│       │   ├── evaluate.py           # RAGAS evaluation script
│       │   ├── eval_dataset.py       # 5 synthetic test cases
│       │   └── eval_results.csv      # Evaluation results
│       ├── server.py                 # FastAPI backend
│       └── index.html                # Frontend UI
├── .env.example                      # API key template
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## RAGAS Evaluation

The retrieval pipeline was evaluated using [RAGAS](https://github.com/explodinggradients/ragas) on 5 synthetic research queries covering topics like Alzheimer's, CRISPR, COVID-19 vaccines, diabetes, and breast cancer immunotherapy.

### Metrics
- **Faithfulness**: How grounded the summary is in the retrieved paper abstracts
- **Answer Relevancy**: How relevant the summary is to the research query

To rerun evaluation:
```bash
python -m src.app.rag.evaluate
```

---

## Technologies Used

- [LangGraph](https://github.com/langchain-ai/langgraph) — multi-agent orchestration
- [HuggingFace Transformers](https://huggingface.co/docs/transformers) — local GPT-2 summarization
- [arXiv API](https://arxiv.org/help/api) — live paper retrieval
- [Groq](https://console.groq.com) — LLaMA 3.1 for RAGAS scoring
- [RAGAS](https://github.com/explodinggradients/ragas) — RAG evaluation framework
- [FastAPI](https://fastapi.tiangolo.com) — backend API
- [Uvicorn](https://www.uvicorn.org) — ASGI server
