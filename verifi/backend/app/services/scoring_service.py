from typing import List
from app.core.enums import VerificationStatus
from app.models.verification import VerificationCheck
from app.models.score import ComplianceScore, ScoreComponent
from app.rules.definitions import RULE_DEFINITIONS
from app.config import settings


class ScoringService:
    def __init__(self):
        self.review_ratio = settings.REVIEW_SCORE_RATIO

    def calculate_score(self, checks: List[VerificationCheck]) -> ComplianceScore:
        passed_count = 0
        failed_count = 0
        review_count = 0
        na_count = 0

        score_components: List[ScoreComponent] = []
        total_awarded = 0.0
        total_possible = 0.0

        for check in checks:
            rule_def = RULE_DEFINITIONS.get(check.rule_code)
            weight = rule_def.weight if rule_def else 10.0

            if check.status == VerificationStatus.PASS:
                passed_count += 1
                points = weight
                total_awarded += points
                total_possible += weight
                notes = "Full compliance verified."
            elif check.status == VerificationStatus.FAIL:
                failed_count += 1
                points = 0.0
                total_awarded += points
                total_possible += weight
                notes = check.reason
            elif check.status == VerificationStatus.REVIEW:
                review_count += 1
                points = weight * self.review_ratio
                total_awarded += points
                total_possible += weight
                notes = f"Partial credit ({int(self.review_ratio * 100)}%) assigned pending manual review: {check.reason}"
            elif check.status == VerificationStatus.NOT_APPLICABLE:
                na_count += 1
                points = 0.0
                # Excluded from denominator
                notes = "Requirement not applicable to this bidder entity."
            else:
                points = 0.0
                total_possible += weight
                notes = "Unrecognized status."

            score_components.append(
                ScoreComponent(
                    requirement_code=check.requirement_code,
                    rule_code=check.rule_code,
                    weight=weight,
                    status=check.status.value,
                    points_awarded=round(points, 2),
                    max_possible_points=weight,
                    notes=notes,
                )
            )

        if total_possible > 0:
            final_score = round((total_awarded / total_possible) * 100.0, 1)
        else:
            final_score = 0.0

        # Bound between 0 and 100
        final_score = max(0.0, min(100.0, final_score))

        return ComplianceScore(
            total_score=final_score,
            passed_count=passed_count,
            failed_count=failed_count,
            review_count=review_count,
            na_count=na_count,
            components=score_components,
        )


scoring_service = ScoringService()
