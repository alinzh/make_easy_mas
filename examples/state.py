from typing import TypedDict, List, Optional
from langchain_core.messages import AnyMessage

class State(TypedDict):
    messages: List[AnyMessage]
    plan: Optional[List[str]]
    draft: Optional[str]
    validated: Optional[bool]
    summary: Optional[str]