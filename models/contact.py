from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BuyingRole(str, Enum):
    CHAMPION = "CHAMPION"
    ECONOMIC_BUYER = "ECONOMIC_BUYER"
    DECISION_MAKER = "DECISION_MAKER"
    INFLUENCER = "INFLUENCER"
    BLOCKER = "BLOCKER"
    USER = "USER"
    UNKNOWN = "UNKNOWN"


class Contact(BaseModel):
    contact_id: str
    account_id: str

    first_name: str
    last_name: str

    title: str
    email: Optional[str] = None

    buying_role: BuyingRole = BuyingRole.UNKNOWN
    seniority: Optional[str] = None

    engagement_score: float = Field(
        default=50,
        ge=0,
        le=100,
    )

    sentiment_score: float = Field(
        default=0,
        ge=-1,
        le=1,
    )

    is_active_in_deal: bool = True

    notes: list[str] = Field(
        default_factory=list,
    )
