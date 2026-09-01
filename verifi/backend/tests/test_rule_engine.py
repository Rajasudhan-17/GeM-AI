import pytest
from app.core.enums import VerificationStatus, DocumentType
from app.rules.engine import rule_engine
from app.providers.base import ProviderVerificationResult


def test_rule_engine_gst_pass():
    doc_facts = {"gstin": "07AABCS1429B1Z1", "status": "ACTIVE"}
    provider_res = ProviderVerificationResult(
        source_name="MOCK_GST",
        status="AVAILABLE",
        is_available=True,
        authoritative_facts={"gstin": "07AABCS1429B1Z1", "registration_status": "ACTIVE"},
    )

    check = rule_engine.evaluate(
        run_id="VR-TEST",
        requirement_code="REQ-GST-001",
        rule_code="GST-001",
        check_name="GST Check",
        document_type=DocumentType.GST,
        document_id="DOC-1",
        doc_facts=doc_facts,
        provider_result=provider_res,
    )

    assert check.status == VerificationStatus.PASS
    assert check.fact_comparison.matched is True


def test_rule_engine_gst_fail_mismatch():
    doc_facts = {"gstin": "07AACPV9821K1Z2", "status": "ACTIVE"}
    provider_res = ProviderVerificationResult(
        source_name="MOCK_GST",
        status="AVAILABLE",
        is_available=True,
        authoritative_facts={"gstin": "07AACPV9821K1ZP", "registration_status": "ACTIVE"},
    )

    check = rule_engine.evaluate(
        run_id="VR-TEST",
        requirement_code="REQ-GST-001",
        rule_code="GST-001",
        check_name="GST Check",
        document_type=DocumentType.GST,
        document_id="DOC-1",
        doc_facts=doc_facts,
        provider_result=provider_res,
    )

    assert check.status == VerificationStatus.FAIL
    assert check.fact_comparison.matched is False
    assert "07AACPV9821K1Z2" in check.reason
    assert "07AACPV9821K1ZP" in check.reason


def test_rule_engine_provider_unavailable_returns_review():
    doc_facts = {"doc_id": "123"}
    provider_res = ProviderVerificationResult(
        source_name="MOCK_DIGILOCKER",
        status="UNAVAILABLE",
        is_available=False,
        authoritative_facts={},
    )

    check = rule_engine.evaluate(
        run_id="VR-TEST",
        requirement_code="REQ-DGL-001",
        rule_code="DGL-001",
        check_name="DigiLocker Check",
        document_type=DocumentType.DIGILOCKER,
        document_id="DOC-1",
        doc_facts=doc_facts,
        provider_result=provider_res,
    )

    # Must be REVIEW, NOT FAIL
    assert check.status == VerificationStatus.REVIEW
    assert "unavailable" in check.reason.lower()
