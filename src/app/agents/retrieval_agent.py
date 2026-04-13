import arxiv
from src.app.graph.state import ResearchState, Paper

client = arxiv.Client()

STUDY_TYPE_KEYWORDS = {
    "clinical trials": "clinical trial randomized",
    "reviews": "systematic review meta-analysis",
    "case studies": "case study case report",
    "any": ""
}

def build_query(state: ResearchState) -> str:
    topic = state.get("topic", "")
    study_type = state.get("study_type", "any").lower()
    time_period = state.get("time_period", "any")
    
    # Map study type to keywords
    study_keywords = STUDY_TYPE_KEYWORDS.get(study_type, "")
    
    # Build query with medical category filter
    query = f"{topic} {study_keywords}".strip()
    return query

def retrieve_papers(state: ResearchState) -> dict:
    query = build_query(state)

    search = arxiv.Search(
        query=query,
        max_results=10,
        sort_by=arxiv.SortCriterion.Relevance,  # Changed from SubmittedDate to Relevance
        sort_order=arxiv.SortOrder.Descending,
        id_list=[],
    )

    papers = []
    for result in client.results(search):
        # Filter to medicine/biology categories
        categories = result.categories
        relevant_cats = [c for c in categories if any(
            c.startswith(prefix) for prefix in ["q-bio", "eess.IV", "cs.CV", "stat.AP", "math.ST"]
        )]
        # Include if relevant category OR topic keyword in title/abstract
        topic = state.get("topic", "").lower()
        if relevant_cats or topic in result.title.lower() or topic in result.summary.lower():
            papers.append(Paper(
                title=result.title,
                authors=", ".join(a.name for a in result.authors[:3]),
                abstract=result.summary[:300] + "...",
                url=result.entry_id,
                paper_id=result.entry_id.split("/")[-1]
            ))

    return {
        "retrieved_papers": papers,
        "retrieval_complete": True,
        "stage": "library"
    }