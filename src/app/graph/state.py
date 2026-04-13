from typing import Optional, List
from typing_extensions import TypedDict

class Paper(TypedDict):
    title: str
    authors: str
    abstract: str
    url: str
    paper_id: str

class ResearchState(TypedDict, total=False):
    # Intake agent fields
    topic: Optional[str]
    time_period: Optional[str]
    study_type: Optional[str]
    current_question: Optional[str]
    current_field: Optional[str]
    intake_complete: bool

    # Retrieval agent fields
    retrieved_papers: Optional[List[Paper]]
    selected_paper_ids: Optional[List[str]]
    retrieval_complete: bool

    # Library agent fields
    saved_papers: Optional[List[Paper]]

    # General
    user_input: Optional[str]
    stage: Optional[str]  # "intake", "retrieval", "library"