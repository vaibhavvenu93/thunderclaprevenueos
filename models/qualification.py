from __future__ import annotations

from pydantic import BaseModel, Field


class Qualification(BaseModel):
    budget_confirmed: bool = False
    budget_range_usd: str | None = None

    authority_confirmed: bool = False
    economic_buyer_identified: bool = False

    business_need_confirmed: bool = False
    quantified_problem: bool = False

    timeline_confirmed: bool = False
    target_decision_date: str | None = None

    decision_process_known: bool = False
    procurement_process_known: bool = False

    competition_known: bool = False
    competitor_names: list[str] = Field(
        default_factory=list,
    )

    champion_identified: bool = False

    success_criteria_defined: bool = False

    qualification_notes: list[str] = Field(
        default_factory=list,
    )
