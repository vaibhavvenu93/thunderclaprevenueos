from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AccountSegment(str, Enum):
    STARTUP = "STARTUP"
    SCALEUP = "SCALEUP"
    MID_MARKET = "MID_MARKET"
    ENTERPRISE = "ENTERPRISE"


class AccountType(str, Enum):
    NEW_LOGO = "NEW_LOGO"
    EXISTING_CUSTOMER = "EXISTING_CUSTOMER"
    PARTNER = "PARTNER"


class Account(BaseModel):
    account_id: str

    company_name: str
    domain: Optional[str] = None

    industry: str
    segment: AccountSegment
    account_type: AccountType

    employee_count: Optional[int] = Field(
        default=None,
        ge=1,
    )

    estimated_revenue_usd: Optional[float] = Field(
        default=None,
        ge=0,
    )

    headquarters_country: Optional[str] = None
    target_market: Optional[str] = None

    strategic_fit_score: float = Field(
        default=50,
        ge=0,
        le=100,
    )

    existing_customer_revenue_usd: float = Field(
        default=0,
        ge=0,
    )

    notes: list[str] = Field(
        default_factory=list,
    )
