from typing import List
from app.core.enums import RiskLevel, VerificationStatus
from app.models.verification import VerificationCheck
from app.models.score import ComplianceScore
from app.models.risk import RiskAssessment, RiskFactor
from app.config import settings


class RiskService:
    def __init__(self):
        self.low_threshold = settings.RISK_THRESHOLD_LOW  # 85.0
        self.medium_threshold = settings.RISK_THRESHOLD_MEDIUM  # 60.0

    def assess_risk(
        self,
        score: ComplianceScore,
        checks: List[VerificationCheck],
    ) -> RiskAssessment:
        risk_factors: List[RiskFactor] = []
        primary_drivers: List[str] = []

        total_score = score.total_score

        # Identify specific risk drivers from failed/review checks
        has_critical_failure = False

        for check in checks:
            if check.status == VerificationStatus.FAIL:
                if check.rule_code == "BL-001":
                    has_critical_failure = True
                    primary_drivers.append("Active Central Debarment / Blacklist Record")
                    risk_factors.append(
                        RiskFactor(
                            category="INTEGRITY_AND_LEGAL",
                            severity="CRITICAL",
                            description=check.reason,
                            impact="Automatic grounds for disqualification under GeM rules.",
                        )
                    )
                elif check.rule_code == "GST-001":
                    primary_drivers.append("GST Registration Discrepancy / Inactivity")
                    risk_factors.append(
                        RiskFactor(
                            category="TAX_COMPLIANCE",
                            severity="HIGH",
                            description=check.reason,
                            impact="Tax invoice non-compliance risk and statutory irregularity.",
                        )
                    )
                elif check.rule_code == "ESIC-001":
                    primary_drivers.append("ESIC Payment Gaps")
                    risk_factors.append(
                        RiskFactor(
                            category="STATUTORY_LABOUR",
                            severity="MEDIUM",
                            description=check.reason,
                            impact="Non-compliance with statutory labor social security mandates.",
                        )
                    )
                elif check.rule_code == "OEM-001":
                    primary_drivers.append("Invalid or Expired OEM Authorization")
                    risk_factors.append(
                        RiskFactor(
                            category="TECHNICAL_ELIGIBILITY",
                            severity="HIGH",
                            description=check.reason,
                            impact="Inability to ensure genuine OEM warranty and hardware support.",
                        )
                    )
                else:
                    primary_drivers.append(f"Failed check: {check.check_name}")
                    risk_factors.append(
                        RiskFactor(
                            category="COMPLIANCE",
                            severity="MEDIUM",
                            description=check.reason,
                            impact="Deficiency in mandatory qualification criteria.",
                        )
                    )
            elif check.status == VerificationStatus.REVIEW:
                if check.rule_code == "OEM-001":
                    risk_factors.append(
                        RiskFactor(
                            category="TECHNICAL_ELIGIBILITY",
                            severity="LOW",
                            description=check.reason,
                            impact="Approaching expiry; requires standard undertaking before PO award.",
                        )
                    )
                elif check.rule_code == "DGL-001":
                    risk_factors.append(
                        RiskFactor(
                            category="SYSTEM_VERIFICATION",
                            severity="LOW",
                            description=check.reason,
                            impact="External gateway downtime; requires visual signature check.",
                        )
                    )

        # Determine composite risk level
        if has_critical_failure or total_score < self.medium_threshold:
            risk_level = RiskLevel.HIGH
        elif total_score < self.low_threshold:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        if not primary_drivers:
            primary_drivers.append("All statutory and technical requirements verified compliant.")

        # Composite risk score (inverse of compliance score, bounded 0-100)
        risk_score = round(max(0.0, 100.0 - total_score), 1)

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            primary_risk_drivers=primary_drivers,
            risk_factors=risk_factors,
        )


risk_service = RiskService()
