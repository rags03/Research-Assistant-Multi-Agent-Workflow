import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from src.app.agents.retrieval_agent import retrieve_papers
from src.app.graph.state import ResearchState
from src.app.rag.eval_dataset import test_cases
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq
import pandas as pd

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

scorer_llm = LangchainLLMWrapper(ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=1024
))
scorer_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
)

def generate_answer(papers: list, query: str) -> str:
    if not papers:
        return "No papers found for this query."
    
    paper_text = "\n\n".join([
        f"Title: {p['title']}\nAuthors: {p['authors']}\nAbstract: {p['abstract']}"
        for p in papers[:3]
    ])

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": """You are a medical research assistant. 
Based on the retrieved papers below, provide a brief summary of what research exists on this topic."""},
            {"role": "user", "content": f"Query: {query}\n\nRetrieved Papers:\n{paper_text}"}
        ]
    )
    return response.choices[0].message.content.strip()

def run_evaluation():
    print("Running evaluation on test cases...\n")

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for i, case in enumerate(test_cases):
        print(f"Processing case {i+1}/{len(test_cases)}: {case['topic']}...")
        
        state = ResearchState(
            topic=case["topic"],
            study_type=case["study_type"],
            time_period=case["time_period"]
        )
        
        result = retrieve_papers(state)
        papers = result.get("retrieved_papers", [])
        
        query = f"{case['topic']} {case['study_type']}"
        answer = generate_answer(papers, query)
        context = "\n".join([p["abstract"] for p in papers[:3]])

        questions.append(query)
        answers.append(answer)
        contexts.append([context])
        ground_truths.append(case["expected"])

        print(f"  Retrieved {len(papers)} papers")

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })

    print("\nRunning RAGAS metrics...")
    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=scorer_llm,
        embeddings=scorer_embeddings
    )

    df = results.to_pandas()
    print("\n--- RAGAS Evaluation Results ---")
    print("Columns:", df.columns.tolist())
    print(df.to_string())

    df.to_csv("src/app/rag/eval_results.csv", index=False)
    print("\nResults saved to src/app/rag/eval_results.csv")

if __name__ == "__main__":
    run_evaluation()