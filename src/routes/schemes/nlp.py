from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0

class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 7
    threshold: Optional[float] = 0.5
    context_aware_answer: Optional[int] = 0
    clear_chat_history: Optional[int] = 0
    cache_do_reset: Optional[int] = 0
    