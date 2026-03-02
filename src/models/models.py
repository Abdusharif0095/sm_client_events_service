from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, BeforeValidator
from typing import Any, Dict, List, Union, Optional, Annotated


def validate_date(value: str):
    try:
        datetime.formatisoformat(value)
    except Exception as e:
        raise ValueError("datetime must be in format YYYY-MM-DDThh:mm:ss±hh:mm")


DateTime = Annotated[str, BeforeValidator(validate_date)]


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


class PingData(BaseModel):
    ping_uuid: str
    user_uuid: str
    ping_device_uuid: str
    ping_time: DateTime


class PingResponse(BaseModel):
    ping_uuid: Optional[str]
    user_uuid: Optional[str]
    ping_device_uuid: Optional[str]
    pong_device_uuid: Optional[str]
    pong_ip_address: Optional[str]
    ping_time: Optional[DateTime]
    pong_time: Optional[DateTime]
    ttl: int = 0 # diff in ms default 0
    comment: Optional[str]