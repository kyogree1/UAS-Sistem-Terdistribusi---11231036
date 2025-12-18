from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Event(BaseModel):
    topic: str
    event_id: str
    timestamp: str
    source: Optional[str] = None
    payload: Dict[str, Any]

class Batch(BaseModel):
    events: List[Event] = Field(min_items=1)
