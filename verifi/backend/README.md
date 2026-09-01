# VERIFI – Backend Engine

Automated Bidder Document and Compliance Verification Engine for GeM and Government Procurement (Phase 1 MVP).

## Features
- **Zero Database Architecture**: In-memory repository abstractions (`TenderRepository`, `BidderRepository`, `BidRepository`, `DocumentRepository`, `VerificationRepository`, `DecisionRepository`, `AuditRepository`) ready for drop-in Phase 2 PostgreSQL replacement.
- **Genuine OCR & Extraction**: PyMuPDF direct text extraction with structured fact parsing and regex classification.
- **Authoritative Mock Government Providers**: GST, Udyam MSME, PAN, EPFO, ESIC, OEM Authorization, DigiLocker, and Central Debarment/Blacklist.
- **Deterministic Rule Engine**: Rules (`GST-001` through `BL-001`) evaluate facts with clear mathematical scoring and configurable risk grading.
- **Grounded Mock AI**: AI Chat and Decision Rationale Generation grounded strictly on backend verification check data without controlling compliance statuses.
- **Immutable Decisions & SHA-256 Chained Audit Trail**: Tamper-evident logging and immutable officer decision history.

## Startup Commands

```bash
# 1. Activate Virtual Environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Seed In-Memory Database & Synthetic Documents
python -m app.seed

# 4. Start FastAPI Server
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

## Running Tests

```bash
python -m pytest tests/ -v
```
