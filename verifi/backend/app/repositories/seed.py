import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.config import settings
from app.core.enums import DocumentType, DocumentStatus
from app.models.tender import Tender
from app.models.requirement import TenderRequirement
from app.models.bidder import Bidder
from app.models.bid import Bid
from app.models.document import Document
from app.dependencies import (
    tender_repo,
    bidder_repo,
    bid_repo,
    document_repo,
    audit_repo,
)
from app.ocr.service import ocr_service
from app.extraction.classifier import classifier
from app.extraction.extractor import structured_extractor


def create_pdf(file_path: Path, title: str, lines: List[str], table_data: List[List[str]] = None):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1A365D"),
        alignment=1,  # Center
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
    )
    
    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=10))

    for line in lines:
        story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 4))

    if table_data:
        story.append(Spacer(1, 10))
        t = Table(table_data, colWidths=[200, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#2D3748")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ]))
        story.append(t)

    doc.build(story)


def generate_synthetic_documents(docs_base: Path):
    # 1. Suresh Enterprises
    suresh_dir = docs_base / "suresh"
    create_pdf(
        suresh_dir / "gst_certificate.pdf",
        "GOVERNMENT OF INDIA - FORM GST REG-06<br/>REGISTRATION CERTIFICATE",
        [
            "<b>Registration Number (GSTIN):</b> 07AABCS1429B1Z1",
            "<b>Legal Name:</b> Suresh Enterprises Pvt Ltd",
            "<b>Trade Name:</b> Suresh Enterprises",
            "<b>Constitution of Business:</b> Private Limited Company",
            "<b>Date of Liability:</b> 2020-04-01",
            "<b>Status:</b> ACTIVE",
            "<b>Jurisdiction:</b> Ward 102, New Delhi, Delhi",
        ],
    )
    create_pdf(
        suresh_dir / "udyam_certificate.pdf",
        "MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES<br/>UDYAM REGISTRATION CERTIFICATE",
        [
            "<b>Udyam Registration Number:</b> UDYAM-DL-01-0019284",
            "<b>Name of Enterprise:</b> Suresh Enterprises Pvt Ltd",
            "<b>Type of Enterprise:</b> SMALL",
            "<b>Major Activity:</b> SERVICES",
            "<b>National Industry Classification Code:</b> 62020 - Information Technology Consulting",
            "<b>Date of Incorporation:</b> 2018-05-12",
        ],
    )
    create_pdf(
        suresh_dir / "pan_card.pdf",
        "INCOME TAX DEPARTMENT - GOVT. OF INDIA<br/>PERMANENT ACCOUNT NUMBER CARD",
        [
            "<b>Permanent Account Number (PAN):</b> AABCS1429B",
            "<b>Name:</b> SURESH ENTERPRISES PVT LTD",
            "<b>Date of Incorporation:</b> 12/05/2018",
            "<b>Entity Category:</b> COMPANY",
        ],
    )
    create_pdf(
        suresh_dir / "epfo_statement.pdf",
        "EMPLOYEES' PROVIDENT FUND ORGANISATION INDIA<br/>ELECTRONIC CHALLAN CUM RETURN (ECR) RECEIPT",
        [
            "<b>Establishment Code:</b> DL/12345/67890",
            "<b>Establishment Name:</b> Suresh Enterprises Pvt Ltd",
            "<b>Wage Month:</b> 2026-01",
            "<b>Payment Status:</b> PAID",
            "<b>Total Contributing Members:</b> 48",
            "<b>Challan Reference Number:</b> TRRN-0019283746",
        ],
    )
    create_pdf(
        suresh_dir / "esic_statement.pdf",
        "EMPLOYEES' STATE INSURANCE CORPORATION<br/>MONTHLY CONTRIBUTION STATEMENT",
        [
            "<b>Employer's Code No.:</b> 11000123450001001",
            "<b>Employer Name:</b> Suresh Enterprises Pvt Ltd",
            "<b>Compliance Period:</b> Jan 2026 to Apr 2026",
            "<b>Jan 2026:</b> PAID",
            "<b>Feb 2026:</b> PAID",
            "<b>Mar 2026:</b> PAID",
            "<b>Apr 2026:</b> PAID",
            "<b>Contribution Status:</b> COMPLIANT",
        ],
    )
    create_pdf(
        suresh_dir / "oem_authorization.pdf",
        "CISCO SYSTEMS INDIA PVT LTD<br/>MANUFACTURER'S AUTHORIZATION FORM (MAF)",
        [
            "<b>From (OEM Name):</b> Cisco Systems India Pvt Ltd",
            "<b>To (Authorized Partner):</b> Suresh Enterprises Pvt Ltd",
            "<b>Tender Number:</b> GEM/2026/B/2317045",
            "<b>Product Category:</b> Networking Switches, Routers & Firewalls",
            "<b>Issued On:</b> 2026-01-15",
            "<b>Valid Until:</b> 2027-01-14",
            "<b>Authorization Scope:</b> Full Manufacturer Warranty & Technical Support for GeM Tender.",
        ],
    )

    # 2. Vikram Traders
    vikram_dir = docs_base / "vikram"
    # CRITICAL: Document GSTIN is 07AACPV9821K1Z2, but Authoritative Source is 07AACPV9821K1ZP
    create_pdf(
        vikram_dir / "gst_certificate_wrong.pdf",
        "GOVERNMENT OF INDIA - FORM GST REG-06<br/>REGISTRATION CERTIFICATE",
        [
            "<b>Registration Number (GSTIN):</b> 07AACPV9821K1Z2",  # WRONG GSTIN!
            "<b>Legal Name:</b> Vikram Traders",
            "<b>Trade Name:</b> Vikram Traders",
            "<b>Constitution of Business:</b> Proprietorship",
            "<b>Date of Liability:</b> 2021-06-15",
            "<b>Status:</b> ACTIVE",
        ],
    )
    # ESIC Gap: Jan 2026 Paid, Feb-Apr 2026 Missing
    create_pdf(
        vikram_dir / "esic_statement_gap.pdf",
        "EMPLOYEES' STATE INSURANCE CORPORATION<br/>MONTHLY CONTRIBUTION STATEMENT",
        [
            "<b>Employer's Code No.:</b> 11000543210001002",
            "<b>Employer Name:</b> Vikram Traders",
            "<b>Contribution Statement Period:</b> Jan 2026 - Apr 2026",
            "<b>Jan 2026:</b> PAID",
            "<b>Feb 2026:</b> MISSING",
            "<b>Mar 2026:</b> MISSING",
            "<b>Apr 2026:</b> MISSING",
            "<b>Note:</b> February 2026 = MISSING, March 2026 = MISSING, April 2026 = MISSING",
        ],
    )
    create_pdf(
        vikram_dir / "udyam_certificate.pdf",
        "MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES<br/>UDYAM REGISTRATION CERTIFICATE",
        [
            "<b>Udyam Registration Number:</b> UDYAM-DL-02-0048192",
            "<b>Name of Enterprise:</b> Vikram Traders",
            "<b>Type of Enterprise:</b> MICRO",
            "<b>Major Activity:</b> TRADING",
        ],
    )
    create_pdf(
        vikram_dir / "pan_card.pdf",
        "INCOME TAX DEPARTMENT - GOVT. OF INDIA<br/>PERMANENT ACCOUNT NUMBER CARD",
        [
            "<b>Permanent Account Number (PAN):</b> AACPV9821K",
            "<b>Name:</b> VIKRAM TRADERS",
            "<b>Entity Category:</b> PROPRIETORSHIP",
        ],
    )
    create_pdf(
        vikram_dir / "epfo_statement.pdf",
        "EMPLOYEES' PROVIDENT FUND ORGANISATION INDIA<br/>ELECTRONIC CHALLAN CUM RETURN (ECR)",
        [
            "<b>Establishment Code:</b> DL/54321/09876",
            "<b>Establishment Name:</b> VIKRAM TRADERS",
            "<b>Wage Month:</b> 2026-01",
            "<b>Payment Status:</b> PAID",
        ],
    )
    create_pdf(
        vikram_dir / "oem_authorization.pdf",
        "D-LINK INDIA LTD<br/>MANUFACTURER'S AUTHORIZATION FORM (MAF)",
        [
            "<b>From (OEM Name):</b> D-Link India Ltd",
            "<b>To (Authorized Partner):</b> Vikram Traders",
            "<b>Tender Number:</b> GEM/2026/B/2317045",
            "<b>Product Category:</b> Enterprise Network Switches & Access Points",
            "<b>Issued On:</b> 2026-01-01",
            "<b>Valid Until:</b> 2026-12-31",
        ],
    )

    # 3. NovaTech Systems (HIGH RISK - Multiple Issues)
    novatech_dir = docs_base / "novatech"
    create_pdf(
        novatech_dir / "gst_certificate_problem.pdf",
        "GOVERNMENT OF INDIA - FORM GST REG-06<br/>REGISTRATION CERTIFICATE",
        [
            "<b>Registration Number (GSTIN):</b> 07AABCN8822M1ZQ",
            "<b>Legal Name:</b> NovaTech Systems",
            "<b>Status:</b> CANCELLED / INACTIVE",
            "<b>Remarks:</b> Registration cancelled by tax authority due to non-filing.",
        ],
    )
    create_pdf(
        novatech_dir / "pan_card_problem.pdf",
        "INCOME TAX DEPARTMENT - GOVT. OF INDIA<br/>PERMANENT ACCOUNT NUMBER CARD",
        [
            "<b>Permanent Account Number (PAN):</b> AACPN9999M",  # Mismatches authoritative AABCN8822M
            "<b>Name:</b> NOVATECH HOLDINGS",
        ],
    )
    create_pdf(
        novatech_dir / "epfo_problem.pdf",
        "EMPLOYEES' PROVIDENT FUND ORGANISATION INDIA<br/>CHALLAN STATEMENT",
        [
            "<b>Establishment Code:</b> DL/99999/00000",
            "<b>Establishment Name:</b> NovaTech Systems",
            "<b>Payment Status:</b> UNPAID / DEFAULT",
        ],
    )
    create_pdf(
        novatech_dir / "oem_authorization_wrong.pdf",
        "HP ENTERPRISE INDIA<br/>RESELLER CERTIFICATE",
        [
            "<b>OEM Name:</b> HP Enterprise India",
            "<b>Authorized Partner:</b> NovaTech Systems",
            "<b>Tender Number:</b> GEM/2025/B/9999999",  # WRONG TENDER
            "<b>Product Scope:</b> Consumer Laptops & Printers Only",  # WRONG PRODUCT SCOPE
            "<b>Valid Until:</b> 2025-12-31",  # EXPIRED
        ],
    )

    # 4. Green Fields Agro Equipment (LOW RISK with OEM Near Expiry REVIEW)
    green_dir = docs_base / "green_fields"
    create_pdf(
        green_dir / "gst_certificate.pdf",
        "GOVERNMENT OF INDIA - FORM GST REG-06<br/>REGISTRATION CERTIFICATE",
        [
            "<b>Registration Number (GSTIN):</b> 07AAACG5541L1Z9",
            "<b>Legal Name:</b> Green Fields Agro Equipment",
            "<b>Trade Name:</b> Green Fields",
            "<b>Status:</b> ACTIVE",
        ],
    )
    create_pdf(
        green_dir / "udyam_certificate.pdf",
        "MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES<br/>UDYAM REGISTRATION CERTIFICATE",
        [
            "<b>Udyam Registration Number:</b> UDYAM-DL-03-0091823",
            "<b>Name of Enterprise:</b> Green Fields Agro Equipment",
            "<b>Type of Enterprise:</b> SMALL",
            "<b>Major Activity:</b> MANUFACTURING",
        ],
    )
    create_pdf(
        green_dir / "pan_card.pdf",
        "INCOME TAX DEPARTMENT - GOVT. OF INDIA<br/>PERMANENT ACCOUNT NUMBER CARD",
        [
            "<b>Permanent Account Number (PAN):</b> AAACG5541L",
            "<b>Name:</b> GREEN FIELDS AGRO EQUIPMENT",
        ],
    )
    create_pdf(
        green_dir / "epfo_statement.pdf",
        "EMPLOYEES' PROVIDENT FUND ORGANISATION INDIA<br/>ELECTRONIC CHALLAN CUM RETURN (ECR)",
        [
            "<b>Establishment Code:</b> DL/77889/11223",
            "<b>Establishment Name:</b> GREEN FIELDS AGRO EQUIPMENT",
            "<b>Wage Month:</b> 2026-01",
            "<b>Payment Status:</b> PAID",
        ],
    )
    create_pdf(
        green_dir / "esic_statement.pdf",
        "EMPLOYEES' STATE INSURANCE CORPORATION<br/>MONTHLY CONTRIBUTION STATEMENT",
        [
            "<b>Employer's Code No.:</b> 11000778890001004",
            "<b>Employer Name:</b> Green Fields Agro Equipment",
            "<b>Jan 2026:</b> PAID",
            "<b>Feb 2026:</b> PAID",
            "<b>Mar 2026:</b> PAID",
            "<b>Apr 2026:</b> PAID",
            "<b>Status:</b> COMPLIANT",
        ],
    )
    # OEM authorization expiring soon: 2026-09-15 (within 15-30 days)
    create_pdf(
        green_dir / "oem_authorization_near_expiry.pdf",
        "UBIQUITI NETWORKS INDIA<br/>MANUFACTURER'S AUTHORIZATION FORM (MAF)",
        [
            "<b>From (OEM Name):</b> Ubiquiti Networks India",
            "<b>To (Authorized Partner):</b> Green Fields Agro Equipment",
            "<b>Tender Number:</b> GEM/2026/B/2317045",
            "<b>Product Scope:</b> Enterprise WiFi & Network Equipment",
            "<b>Issued On:</b> 2025-09-16",
            "<b>Valid Until:</b> 2026-09-15",
            "<b>Status:</b> Valid but approaching annual renewal window.",
        ],
    )


async def seed_database_and_documents():
    docs_base = settings.MOCK_DATA_DIR / "documents"
    generate_synthetic_documents(docs_base)

    # 1. Tender
    tender = Tender(
        id="TND-001",
        tender_number="GEM/2026/B/2317045",
        title="Supply of Networking Equipment",
        category="IT & Networking Hardware",
        description="Procurement of Enterprise Layer-3 Managed Switches, Routers, and Optical Transceivers for Government Data Centers.",
        organization="Government e-Marketplace (GeM)",
        estimated_value_inr=15000000.0,
    )
    await tender_repo.save(tender)

    # 2. Requirements (8 total, 100 max points)
    requirements_data = [
        ("REQ-GST-001", "GST Registration Compliance", DocumentType.GST, "GST-001", 15.0, "Valid active GSTIN registration."),
        ("REQ-UDYAM-001", "MSME Udyam Registration", DocumentType.UDYAM, "UDYAM-001", 10.0, "Verified MSME Udyam registration certificate."),
        ("REQ-PAN-001", "Income Tax PAN Card", DocumentType.PAN, "PAN-001", 15.0, "Valid PAN card matching company identity."),
        ("REQ-EPFO-001", "EPFO Establishment Compliance", DocumentType.EPFO, "EPFO-001", 10.0, "Active EPFO establishment code and recent electronic challan remittance."),
        ("REQ-ESIC-001", "ESIC Contribution Compliance", DocumentType.ESIC, "ESIC-001", 10.0, "ESIC monthly contributions without gaps."),
        ("REQ-OEM-001", "OEM Manufacturer Authorization (MAF)", DocumentType.OEM, "OEM-001", 15.0, "Direct OEM Authorization letter covering tender scope and warranty."),
        ("REQ-DGL-001", "DigiLocker Digital Verification", DocumentType.DIGILOCKER, "DGL-001", 10.0, "Cryptographic digital verification of credentials."),
        ("REQ-BL-001", "Non-Debarment / Blacklist Clearance", DocumentType.BLACKLIST, "BL-001", 15.0, "Clear verification against Central Debarment Database."),
    ]

    for req_code, name, doc_type, rule_code, weight, desc in requirements_data:
        req = TenderRequirement(
            id=f"TREQ-{req_code}",
            tender_id=tender.id,
            code=req_code,
            name=name,
            document_type=doc_type,
            rule_code=rule_code,
            is_mandatory=True,
            weight=weight,
            description=desc,
        )
        await tender_repo.save_requirement(req)

    # 3. Bidders
    bidders_data = [
        {
            "id": "BDR-77291",
            "name": "Suresh Enterprises Pvt Ltd",
            "legal_entity_type": "Private Limited Company",
            "primary_email": "contact@sureshenterprises.com",
            "primary_phone": "+91-9810012345",
            "registered_address": "Plot 42, Okhla Industrial Area Phase-III, New Delhi 110020",
            "pan": "AABCS1429B",
            "gstin": "07AABCS1429B1Z1",
            "udyam_number": "UDYAM-DL-01-0019284",
            "bid_id": "BID-77291",
            "folder": "suresh",
        },
        {
            "id": "BDR-51064",
            "name": "Vikram Traders",
            "legal_entity_type": "Proprietorship",
            "primary_email": "vikram.traders.delhi@gmail.com",
            "primary_phone": "+91-9871154321",
            "registered_address": "Shop 14, Nehru Place Commercial Complex, New Delhi 110019",
            "pan": "AACPV9821K",
            "gstin": "07AACPV9821K1ZP",  # Note: Authoritative GSTIN
            "udyam_number": "UDYAM-DL-02-0048192",
            "bid_id": "BID-51064",
            "folder": "vikram",
        },
        {
            "id": "BDR-90218",
            "name": "NovaTech Systems",
            "legal_entity_type": "Private Limited Company",
            "primary_email": "admin@novatechsystems.in",
            "primary_phone": "+91-9999088218",
            "registered_address": "Unit 8, Tech Park Sector 62, Noida 201301",
            "pan": "AABCN8822M",
            "gstin": "07AABCN8822M1ZQ",
            "udyam_number": "",
            "bid_id": "BID-90218",
            "folder": "novatech",
        },
        {
            "id": "BDR-63357",
            "name": "Green Fields Agro Equipment",
            "legal_entity_type": "Partnership Firm",
            "primary_email": "sales@greenfieldsagro.co.in",
            "primary_phone": "+91-9811263357",
            "registered_address": "Industrial Area, Bawana Phase-1, Delhi 110039",
            "pan": "AAACG5541L",
            "gstin": "07AAACG5541L1Z9",
            "udyam_number": "UDYAM-DL-03-0091823",
            "bid_id": "BID-63357",
            "folder": "green_fields",
        },
    ]

    for b_data in bidders_data:
        bidder = Bidder(
            id=b_data["id"],
            name=b_data["name"],
            legal_entity_type=b_data["legal_entity_type"],
            primary_email=b_data["primary_email"],
            primary_phone=b_data["primary_phone"],
            registered_address=b_data["registered_address"],
            pan=b_data["pan"],
            gstin=b_data["gstin"],
            udyam_number=b_data["udyam_number"],
        )
        await bidder_repo.save(bidder)

        bid = Bid(
            id=b_data["bid_id"],
            tender_id=tender.id,
            bidder_id=bidder.id,
            bid_number=f"BID-{tender.tender_number.split('/')[-1]}-{bidder.id.split('-')[-1]}",
            status="SUBMITTED",
        )
        await bid_repo.save(bid)

        # Attach synthetic PDF documents to bid
        bidder_folder = docs_base / b_data["folder"]
        if bidder_folder.exists():
            for pdf_file in bidder_folder.glob("*.pdf"):
                with open(pdf_file, "rb") as pf:
                    content = pf.read()
                
                text, method = ocr_service.process_document(content, pdf_file.name)
                doc_type = classifier.classify(text, pdf_file.name)
                extracted_facts = structured_extractor.extract(text, doc_type)

                doc = Document(
                    id=f"DOC-{pdf_file.stem}_{b_data['id']}",
                    bid_id=bid.id,
                    bidder_id=bidder.id,
                    file_name=pdf_file.name,
                    original_file_name=pdf_file.name,
                    file_path=str(pdf_file),
                    file_size_bytes=len(content),
                    mime_type="application/pdf",
                    document_type=doc_type,
                    status=DocumentStatus.PROCESSED,
                    ocr_text=text,
                    extracted_facts=extracted_facts,
                    metadata={"ocr_method": method},
                )
                await document_repo.save(doc)


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database_and_documents())
    print("Seed data and synthetic PDF documents successfully generated.")
