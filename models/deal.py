from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from models.qualification import Qualification


class DealStage(str, Enum):
    INBOUND = "INBOUND"
    QUALIFIED = "QUALIFIED"
    DISCOVERY = "DISCOVERY"
    SOLUTION = "SOLUTION"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CONTRACT = "CONTRACT"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class ServiceLine(str, Enum):
    POSITIONING = "POSITIONING"
    BRANDING = "BRANDING"
    WEBSITE_DESIGN = "WEBSITE_DESIGN"
    WEBSITE_DEVELOPMENT = "WEBSITE_DEVELOPMENT"
    WEBSITE_AND_BRAND = "WEBSITE_AND_BRAND"
    GROWTH_OPTIMISATION = "GROWTH_OPTIMISATION"
    OTHER = "OTHER"


class DealSource(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    REFERRAL = "REFERRAL"
    EXISTING_ACCOUNT = "EXISTING_ACCOUNT"
    PARTNER = "PARTNER"


class ForecastCategory(str, Enum):
    PIPELINE = "PIPELINE"
    UPSIDE = "UPSIDE"
    LIKELY = "LIKELY"
    COMMIT = "COMMIT"
    CLOSED = "CLOSED"


class Deal(BaseModel):
    deal_id: str
    account_id: str

    deal_name: str

    stage: DealStage
    forecast_category: ForecastCategory

    service_line: ServiceLine
    source: DealSource

    amount_usd: float = Field(
        ge=0,
    )

    probability: float = Field(
        default=0.25,
        ge=0,
        le=1,
    )

    owner: str

    created_date: date
    expected_close_date: date

    last_meaningful_activity_date: date

    next_meeting_date: Optional[date] = None
    proposal_sent_date: Optional[date] = None

    days_in_stage: int = Field(
        default=0,
        ge=0,
    )

    founder_involved: bool = False

    qualification: Qualification

    primary_objection: Optional[str] = None
    competitor: Optional[str] = None

    commercial_risk: Optional[str] = None
    delivery_risk: Optional[str] = None

    next_step: Optional[str] = None
    lost_reason: Optional[str] = None

    notes: list[str] = Field(
        default_factory=list,
    )
