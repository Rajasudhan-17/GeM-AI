import pytest
from app.config import settings
from app.ocr.service import ocr_service
from app.extraction.classifier import classifier
from app.extraction.extractor import structured_extractor
from app.core.enums import DocumentType


def test_ocr_and_extraction_suresh_gst():
    pdf_path = settings.MOCK_DATA_DIR / "documents" / "suresh" / "gst_certificate.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    text, method = ocr_service.process_document(pdf_bytes, pdf_path.name)
    assert len(text) > 20
    assert "07AABCS1429B1Z1" in text

    doc_type = classifier.classify(text, pdf_path.name)
    assert doc_type == DocumentType.GST

    facts = structured_extractor.extract(text, doc_type)
    assert facts["gstin"] == "07AABCS1429B1Z1"
    assert "Suresh Enterprises" in facts["legal_name"]
    assert facts["status"] == "ACTIVE"


def test_ocr_and_extraction_vikram_wrong_gst():
    pdf_path = settings.MOCK_DATA_DIR / "documents" / "vikram" / "gst_certificate_wrong.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    text, _ = ocr_service.process_document(pdf_bytes, pdf_path.name)
    assert "07AACPV9821K1Z2" in text

    doc_type = classifier.classify(text, pdf_path.name)
    assert doc_type == DocumentType.GST

    facts = structured_extractor.extract(text, doc_type)
    assert facts["gstin"] == "07AACPV9821K1Z2"


def test_ocr_and_extraction_vikram_esic_gap():
    pdf_path = settings.MOCK_DATA_DIR / "documents" / "vikram" / "esic_statement_gap.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    text, _ = ocr_service.process_document(pdf_bytes, pdf_path.name)
    doc_type = classifier.classify(text, pdf_path.name)
    assert doc_type == DocumentType.ESIC

    facts = structured_extractor.extract(text, doc_type)
    assert "2026-02" in facts["missing_months"]
    assert "2026-03" in facts["missing_months"]
    assert "2026-04" in facts["missing_months"]
    assert facts["status"] == "GAPS_DETECTED"
