from src.app.graph.state import ResearchState

INTAKE_QUESTIONS = [
    ("topic", "What medical or biology topic are you researching? (e.g. cancer immunotherapy, CRISPR, Alzheimer's)"),
    ("time_period", "What time period are you interested in? (e.g. last 1 year, last 5 years, any)"),
    ("study_type", "What type of research are you looking for? (e.g. clinical trials, reviews, case studies, any)"),
]

def ask_intake_question(state: ResearchState) -> dict:
    for field, question in INTAKE_QUESTIONS:
        if state.get(field) is None:
            return {
                "current_question": question,
                "current_field": field,
                "intake_complete": False,
                "stage": "intake"
            }
    return {
        "current_question": None,
        "intake_complete": True,
        "stage": "retrieval"
    }

def record_intake_answer(state: ResearchState) -> dict:
    field = state.get("current_field")
    user_input = state.get("user_input")
    return {field: user_input, "user_input": None}