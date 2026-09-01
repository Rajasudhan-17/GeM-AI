import asyncio
from app.config import settings
from app.ocr.service import ocr_service
from app.extraction.classifier import classifier
from app.extraction.extractor import structured_extractor
from app.providers.gst import MockGSTProvider
from app.rules.engine import rule_engine
from app.core.enums import VerificationStatus, DocumentType


def test_vikram_gst_mismatch(client):
    """
    CRITICAL TEST:
    1. Read synthetic PDF for Vikram Traders: gst_certificate_wrong.pdf
    2. Run PyMuPDF direct text extraction
    3. Extract document GSTIN -> 07AACPV9821K1Z2
    4. Call MockGSTProvider for bidder BDR-51064 -> returns authoritative 07AACPV9821K1ZP
    5. Evaluate GST-001 rule
    6. Assert result == FAIL
    7. Assert reason explains the exact mismatch
    """
    pdf_path = settings.MOCK_DATA_DIR / "documents" / "vikram" / "gst_certificate_wrong.pdf"
    assert pdf_path.exists(), f"File {pdf_path} must exist"

    # Step 1 & 2: OCR / Text extraction
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    ocr_text, _ = ocr_service.process_document(pdf_bytes, pdf_path.name)
    assert "07AACPV9821K1Z2" in ocr_text

    # Step 3: Classification & Structured Extraction
    doc_type = classifier.classify(ocr_text, pdf_path.name)
    assert doc_type == DocumentType.GST

    extracted_facts = structured_extractor.extract(ocr_text, doc_type)
    document_gstin = extracted_facts.get("gstin")
    assert document_gstin == "07AACPV9821K1Z2"

    # Step 4: Query Mock GST Provider for Vikram Traders (BDR-51064)
    gst_provider = MockGSTProvider()
    provider_result = asyncio.run(gst_provider.verify(bidder_id="BDR-51064", extracted_facts=extracted_facts))
    authoritative_gstin = provider_result.authoritative_facts.get("gstin")
    assert authoritative_gstin == "07AACPV9821K1ZP"

    # Verify that document GSTIN is strictly not equal to source GSTIN
    assert document_gstin != authoritative_gstin

    # Step 5: Evaluate GST-001 Rule
    check = rule_engine.evaluate(
        run_id="VR-VIKRAM-TEST",
        requirement_code="REQ-GST-001",
        rule_code="GST-001",
        check_name="GST Registration Compliance",
        document_type=DocumentType.GST,
        document_id="DOC-VIKRAM-GST",
        doc_facts=extracted_facts,
        provider_result=provider_result,
    )

    # Step 6 & 7: Assert outcomes
    assert check.status == VerificationStatus.FAIL
    assert check.fact_comparison.matched is False
    assert "07AACPV9821K1Z2" in check.reason
    assert "07AACPV9821K1ZP" in check.reason
    assert "does not match authoritative" in check.reason.lower()
