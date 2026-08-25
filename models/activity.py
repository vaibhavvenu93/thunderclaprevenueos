from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ActivityType(str, Enum):
    DISCOVERY_CALL = "DISCOVERY_CALL"
    DEMO = "DEMO"
    EMAIL_SENT = "EMAIL_SENT"
    EMAIL_RECEIVED = "EMAIL_RECEIVED"
    PROPOSAL_SENT = "PROPOSAL_SENT"
    FOLLOW_UP = "FOLLOW_UP"
    NEGOTIATION_CALL = "NEGOTIATION_CALL"
    INTERNAL_REVIEW = "INTERNAL_REVIEW"
    CUSTOMER_MEETING = "CUSTOMER_MEETING"
    CONTRACT_SENT = "CONTRACT_SENT"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class ActivityDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    INTERNAL = "INTERNAL"


class Activity(BaseModel):
    activity_id: str
    deal_id: str

    activity_type: ActivityType
    direction: ActivityDirection

    timestamp: datetime

    contact_id: Optional[str] = None
    owner: Optional[str] = None

    summary: str

    transcript: Optional[str] = None
    email_body: Optional[str] = None

    next_step: Optional[str] = None

    requires_follow_up: bool = False
