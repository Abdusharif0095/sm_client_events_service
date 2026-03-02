from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Union, Optional


class EventModel(BaseModel):
    transaction_id: str
    event_type: str
    payload: Dict[str, Union[Optional[str], Optional[int], Optional[float], Optional[bool], Optional[List[Any]], Optional[Dict]]] = Field(default_factory=dict,
                                                                                                                          description="JSON of arguments")
    

class Layer(str, Enum):
    db = "db"
    python = "python"


class Alert(BaseModel):
    layer: Layer
    service: str
    function: str
    error: str
    datetime: str
    comment: Optional[str] = None
