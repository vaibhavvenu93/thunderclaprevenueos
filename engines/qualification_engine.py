from __future__ import annotations

from dataclasses import dataclass

from models.deal import Deal


@dataclass
class QualificationAssessment:
    score: float
    grade: str

    completed_signals: int
    total_signals: int

    missing_signals: list[str]

    forecast_multiplier: float
    confidence: float


QUALIFICATION_SIGNALS = {
    "budget_confirmed": "Budget confirmed",
    "authority_confirmed": "Authority confirmed",
    "economic_buyer_identified": "Economic buyer identified",
    "business_need_confirmed": "Business need confirmed",
    "quantified_problem": "Problem quantified",
    "timeline_confirmed": "Timeline confirmed",
    "decision_process_known": "Decision process known",
    "procurement_process_known": "Procurement process known",
    "champion_identified": "Champion identified",
    "success_criteria_defined": "Success criteria defined",
}


SIGNAL_WEIGHTS = {
    "budget_confirmed": 12,
    "authority_confirmed": 8,
    "economic_buyer_identified": 14,
    "business_need_confirmed": 12,
    "quantified_problem": 10,
    "timeline_confirmed": 10,
    "decision_process_known": 12,
    "procurement_process_known": 6,
    "champion_identified": 10,
    "success_criteria_defined": 6,
}


def _grade(score: float) -> str:
    if score >= 85:
        return "A"

    if score >= 70:
        return "B"

    if score >= 55:
        return "C"

    if score >= 40:
        return "D"

    return "F"


def _forecast_multiplier(score: float) -> float:
    """
    Reduce forecast confidence when qualification quality is weak.

    A deal can still have a high salesperson-entered probability,
    but weak qualification should reduce how much of that probability
    the Revenue OS trusts.
    """

    if score >= 85:
        return 1.00

    if score >= 70:
        return 0.90

    if score >= 55:
        return 0.75

    if score >= 40:
        return 0.55

    return 0.35


def assess_qualification(
    deal: Deal,
) -> QualificationAssessment:

    qualification = deal.qualification

    achieved_weight = 0
    total_weight = sum(
        SIGNAL_WEIGHTS.values()
    )

    completed_signals = 0
    missing_signals: list[str] = []

    for field_name, label in QUALIFICATION_SIGNALS.items():

        value = getattr(
            qualification,
            field_name,
        )

        if value:
            achieved_weight += SIGNAL_WEIGHTS[
                field_name
            ]

            completed_signals += 1

        else:
            missing_signals.append(
                label
            )

    score = (
        achieved_weight
        / total_weight
        * 100
    )

    multiplier = _forecast_multiplier(
        score
    )

    confidence = min(
        0.98,
        0.45
        + (
            score / 100
            * 0.50
        ),
    )

    return QualificationAssessment(
        score=round(
            score,
            2,
        ),
        grade=_grade(
            score
        ),

        completed_signals=completed_signals,
        total_signals=len(
            QUALIFICATION_SIGNALS
        ),

        missing_signals=missing_signals,

        forecast_multiplier=round(
            multiplier,
            2,
        ),

        confidence=round(
            confidence,
            2,
        ),
    )


def adjusted_probability(
    deal: Deal,
) -> float:
    """
    Apply qualification quality to the salesperson-entered
    probability to create a more disciplined forecast probability.
    """

    assessment = assess_qualification(
        deal
    )

    return round(
        deal.probability
        * assessment.forecast_multiplier,
        4,
    )
