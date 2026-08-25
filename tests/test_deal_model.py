from datetime import date

import pytest
from pydantic import ValidationError

from models.deal import (
    Deal,
    DealSource,
    DealStage,
    ForecastCategory,
    ServiceLine,
)
from models.qualification import Qualification


def build_test_deal() -> Deal:
    qualification = Qualification(
        budget_confirmed=True,
        authority_confirmed=True,
        economic_buyer_identified=True,
        business_need_confirmed=True,
        quantified_problem=True,
        timeline_confirmed=True,
        decision_process_known=False,
        procurement_process_known=False,
        competition_known=True,
        competitor_names=["Agency X"],
        champion_identified=True,
        success_criteria_defined=True,
    )

    return Deal(
        deal_id="TC-0001",
        account_id="ACC-0001",
        deal_name="Synthetic Website Transformation",

        stage=DealStage.PROPOSAL,
        forecast_category=ForecastCategory.UPSIDE,

        service_line=ServiceLine.WEBSITE_AND_BRAND,
        source=DealSource.INBOUND,

        amount_usd=68000,
        probability=0.55,

        owner="AE-01",

        created_date=date(2026, 7, 15),
        expected_close_date=date(2026, 9, 15),
        last_meaningful_activity_date=date(2026, 8, 18),

        proposal_sent_date=date(2026, 8, 17),
        next_meeting_date=None,

        days_in_stage=8,

        founder_involved=True,

        qualification=qualification,

        primary_objection="Internal stakeholder alignment",
        competitor="Agency X",

        next_step="Re-engage champion and secure decision meeting",
    )


def test_deal_can_be_created():
    deal = build_test_deal()

    assert deal.deal_id == "TC-0001"
    assert deal.amount_usd == 68000
    assert deal.stage == DealStage.PROPOSAL


def test_deal_preserves_qualification():
    deal = build_test_deal()

    assert deal.qualification.budget_confirmed is True
    assert deal.qualification.champion_identified is True
    assert deal.qualification.decision_process_known is False


def test_deal_can_capture_founder_involvement():
    deal = build_test_deal()

    assert deal.founder_involved is True


def test_probability_must_be_valid():
    deal = build_test_deal()

    payload = deal.model_dump()
    payload["probability"] = 1.25

    with pytest.raises(ValidationError):
        Deal.model_validate(payload)


def test_negative_deal_value_is_rejected():
    deal = build_test_deal()

    payload = deal.model_dump()
    payload["amount_usd"] = -5000

    with pytest.raises(ValidationError):
        Deal.model_validate(payload)
