import pytest
from datetime import datetime, timezone
from app.core.enums import VerificationStatus, RiskLevel, DocumentType
from app.models.verification import VerificationCheck
from app.services.scoring_service import scoring_service
from app.services.risk_service import risk_service


def test_score_and_risk_all_pass():
    checks = [
        VerificationCheck(
            id=f"CHK-{i}",
            run_id="VR-1",
            requirement_code=f"REQ-{code}",
            rule_code=code,
            check_name=f"{code} Check",
            document_type=DocumentType.GST,
            status=VerificationStatus.PASS,
            reason="Verified compliant",
            evaluated_at=datetime.now(timezone.utc),
        )
        for i, code in enumerate(["GST-001", "UDYAM-001", "PAN-001", "EPFO-001", "ESIC-001", "OEM-001", "DGL-001", "BL-001"])
    ]

    score = scoring_service.calculate_score(checks)
    assert score.total_score == 100.0
    assert score.passed_count == 8
    assert score.failed_count == 0

    risk = risk_service.assess_risk(score, checks)
    assert risk.risk_level == RiskLevel.LOW
    assert risk.risk_score == 0.0


def test_score_and_risk_with_failures():
    # 2 failures (GST 15 + ESIC 10) -> score 75/100 -> Medium Risk
    checks = [
        VerificationCheck(
            id="CHK-1",
            run_id="VR-1",
            requirement_code="REQ-GST-001",
            rule_code="GST-001",
            check_name="GST Check",
            document_type=DocumentType.GST,
            status=VerificationStatus.FAIL,
            reason="GST Mismatch",
            evaluated_at=datetime.now(timezone.utc),
        ),
        VerificationCheck(
            id="CHK-2",
            run_id="VR-1",
            requirement_code="REQ-ESIC-001",
            rule_code="ESIC-001",
            check_name="ESIC Check",
            document_type=DocumentType.ESIC,
            status=VerificationStatus.FAIL,
            reason="ESIC Gaps",
            evaluated_at=datetime.now(timezone.utc),
        ),
        VerificationCheck(
            id="CHK-3",
            run_id="VR-1",
            requirement_code="REQ-PAN-001",
            rule_code="PAN-001",
            check_name="PAN Check",
            document_type=DocumentType.PAN,
            status=VerificationStatus.PASS,
            reason="Valid",
            evaluated_at=datetime.now(timezone.utc),
        ),
        VerificationCheck(
            id="CHK-4",
            run_id="VR-1",
            requirement_code="REQ-UDYAM-001",
            rule_code="UDYAM-001",
            check_name="Udyam Check",
            document_type=DocumentType.UDYAM,
            status=VerificationStatus.PASS,
            reason="Valid",
            evaluated_at=datetime.now(timezone.utc),
        ),
        VerificationCheck(
            id="CHK-5",
            run_id="VR-1",
            requirement_code="REQ-EPFO-001",
            rule_code="EPFO-001",
            check_name="EPFO Check",
            document_type=DocumentType.EPFO,
            status=VerificationStatus.PASS,
            reason="Valid",
            evaluated_at=datetime.now(timezone.utc),
        ),
        VerificationCheck(
            id="CHK-6",
            run_id="VR-1",
            requirement_code="REQ-OEM-001",
            rule_code="OEM-001",
            check_name="OEM Check",
            document_type=DocumentType.OEM,
            status=VerificationStatus.PASS,
            reason="Valid",
            evaluated_at=datetime.now(timezone.utc),
        ),
        VerificationCheck(
            id="CHK-7",
            run_id="VR-1",
            requirement_code="REQ-DGL-001",
            rule_code="DGL-001",
            check_name="DigiLocker Check",
            document_type=DocumentType.DIGILOCKER,
            status=VerificationStatus.PASS,
            reason="Valid",
            evaluated_at=datetime.now(timezone.utc),
        ),
        VerificationCheck(
            id="CHK-8",
            run_id="VR-1",
            requirement_code="REQ-BL-001",
            rule_code="BL-001",
            check_name="Blacklist Check",
            document_type=DocumentType.BLACKLIST,
            status=VerificationStatus.PASS,
            reason="Clear",
            evaluated_at=datetime.now(timezone.utc),
        ),
    ]

    score = scoring_service.calculate_score(checks)
    assert score.total_score == 75.0
    assert score.passed_count == 6
    assert score.failed_count == 2

    risk = risk_service.assess_risk(score, checks)
    assert risk.risk_level == RiskLevel.MEDIUM
