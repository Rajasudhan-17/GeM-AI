# VERIFI – GeM Bid Compliance Verification Engine

VERIFI is an automated verification and compliance engine designed for government procurement on the Government e-Marketplace (GeM).

## System Architecture

```
Document Upload (PDF/Images)
        ↓
OCR & Text Extraction (PyMuPDF)
        ↓
Document Classification (GST, Udyam, PAN, EPFO, ESIC, OEM, DigiLocker, Blacklist)
        ↓
Structured Data Extraction (Facts Parsing)
        ↓
Mock Government Source Verification (Authoritative Cross-Check)
        ↓
Fact Comparison Layer (Discrepancy Detection)
        ↓
Deterministic Compliance Rules (GST-001 ... BL-001)
        ↓
Outcomes (PASS / FAIL / REVIEW / NOT_APPLICABLE)
        ↓
Compliance Score (Dynamic Weighted Scoring / 100)
        ↓
Risk Assessment (LOW / MEDIUM / HIGH)
        ↓
AI Grounded Explanation & Chat Assistant
        ↓
Officer Review & Auto-Drafted Rationale
        ↓
Accept / Reject Submission
        ↓
Immutable Decision History & SHA-256 Chained Audit Trail
```

## Project Structure

```
verifi/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entrypoint & lifespan
│   │   ├── config.py            # Pydantic Settings configuration
│   │   ├── api/                 # API endpoint routers (REST v1)
│   │   ├── core/                # Enums, Exceptions, Structured Logger
│   │   ├── models/              # Domain entities
│   │   ├── schemas/             # Pydantic DTO schemas
│   │   ├── repositories/        # Repository interfaces & In-Memory stores
│   │   ├── storage/             # Document storage abstraction (Local/MinIO)
│   │   ├── ocr/                 # PyMuPDF OCR & text extractor
│   │   ├── extraction/          # Document Classifier & Structured Fact Extractor
│   │   ├── providers/           # 8 Authoritative Mock Government Providers
│   │   ├── rules/               # Deterministic Rules (GST-001, etc.) & Evaluator
│   │   ├── ai/                  # Mock AI Provider, Explanation, Chat, Reason Gen
│   │   ├── services/            # Scoring, Risk, Verification, Decision, Audit
│   │   ├── workers/             # Background Job Queue (Local/Celery)
│   │   └── dependencies.py      # Dependency Injection Providers
│   ├── mock_data/               # JSON mock databases & synthetic PDF files
│   ├── tests/                   # 21 unit & end-to-end pytest tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # Production React + TypeScript + Vite + Tailwind UI
│   ├── src/
│   │   ├── api/client.ts        # Centralized API client (VITE_API_URL)
│   │   ├── api/types.ts         # TypeScript API interfaces
│   │   ├── components/          # Modular Dashboard, Checks, AI, Decisions, Audit
│   │   └── App.tsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── test-ui/                     # Backend Diagnostic Console (Vanilla JS/HTML)
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── README.md
```

## Quick Start Instructions

### 1. Start Backend

```bash
cd verifi/backend
python -m app.seed
uvicorn app.main:app --reload --port 8000
```
- API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 2. Start Main Production Frontend (React + TypeScript)

In a separate terminal:
```bash
cd verifi/frontend
npm install
npm run dev
```
- Open Main Application: [http://localhost:5173](http://localhost:5173)

### 3. Start Test UI Console (Diagnostic Console)

In a separate terminal:
```bash
cd verifi
python -m http.server 5500 --directory test-ui
```
- Open Test Console in Browser: [http://localhost:5500](http://localhost:5500)

### 4. Run Automated Tests

```bash
cd verifi/backend
python -m pytest tests/ -v
```

## Four Primary MVP Demo Bidders

1. **Suresh Enterprises Pvt Ltd (`BDR-77291`)**
   - Expected: `100.0%` Compliance, `LOW RISK`
   - All statutory credentials (GST, PAN, Udyam, EPFO, ESIC) and Cisco OEM MAF are valid and verified.

2. **Vikram Traders (`BDR-51064`)**
   - Expected: `75.0%` Compliance, `MEDIUM RISK`
   - **Critical Mismatch**: Document GSTIN `07AACPV9821K1Z2` != Authoritative GST record `07AACPV9821K1ZP` -> `FAIL` on `GST-001`.
   - **ESIC Gap**: Statement missing Feb, Mar, Apr 2026 -> `FAIL` on `ESIC-001`.

3. **NovaTech Systems (`BDR-90218`)**
   - Expected: High Risk with Multiple Failures.
   - Cancelled GSTIN, PAN mismatch, invalid EPFO, expired HP OEM MAF for consumer laptops, DigiLocker gateway 503 outage (`REVIEW`), and active GeM central debarment/blacklist record (`FAIL` on `BL-001`).

4. **Green Fields Agro Equipment (`BDR-63357`)**
   - Expected: `88-92%` Compliance, `LOW RISK`
   - Ubiquiti OEM Authorization is authentic and valid, but expiring within 15 days (`2026-09-15`) -> triggers `OEM-001` `REVIEW` flag. Demonstrates that a review flag does not cause automatic disqualification.

## Phase 2 Database Integration Plan

In Phase 2, the in-memory repositories in `app/repositories/memory.py` will be mirrored by `app/repositories/postgres.py` using SQLAlchemy 2.0 / asyncpg:
- `PostgresTenderRepository(TenderRepository)`
- `PostgresBidderRepository(BidderRepository)`
- `PostgresBidRepository(BidRepository)`
- `PostgresDocumentRepository(DocumentRepository)`
- `PostgresVerificationRepository(VerificationRepository)`
- `PostgresDecisionRepository(DecisionRepository)`
- `PostgresAuditRepository(AuditRepository)`

The business logic services (`VerificationService`, `ScoringService`, `DecisionService`, `AuditService`, etc.) depend purely on the abstract interfaces in `app/repositories/base.py` and will require zero modifications.
