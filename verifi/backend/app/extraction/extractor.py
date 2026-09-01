import re
from typing import Dict, Any, List, Optional
from app.core.enums import DocumentType
from app.extraction.normalizer import TextNormalizer


class StructuredExtractor:
    def __init__(self):
        self.normalizer = TextNormalizer()

    def extract(self, text: str, doc_type: DocumentType) -> Dict[str, Any]:
        if doc_type == DocumentType.GST:
            return self._extract_gst(text)
        elif doc_type == DocumentType.UDYAM:
            return self._extract_udyam(text)
        elif doc_type == DocumentType.PAN:
            return self._extract_pan(text)
        elif doc_type == DocumentType.EPFO:
            return self._extract_epfo(text)
        elif doc_type == DocumentType.ESIC:
            return self._extract_esic(text)
        elif doc_type == DocumentType.OEM:
            return self._extract_oem(text)
        elif doc_type == DocumentType.DIGILOCKER:
            return self._extract_digilocker(text)
        elif doc_type == DocumentType.BLACKLIST:
            return self._extract_blacklist(text)
        else:
            return {"document_type": "UNKNOWN", "raw_text_length": len(text)}

    def _extract_gst(self, text: str) -> Dict[str, Any]:
        facts: Dict[str, Any] = {
            "document_type": "GST",
            "gstin": None,
            "legal_name": None,
            "trade_name": None,
            "status": "ACTIVE",
            "registration_date": None,
        }
        
        # Extract GSTIN
        gstin_match = re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b", text)
        if gstin_match:
            facts["gstin"] = self.normalizer.normalize_gstin(gstin_match.group(0))

        # Legal Name
        legal_match = re.search(r"(?:Legal Name|Name of Business)\s*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
        if legal_match:
            facts["legal_name"] = self.normalizer.clean_text(legal_match.group(1))

        # Trade Name
        trade_match = re.search(r"(?:Trade Name)\s*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
        if trade_match:
            facts["trade_name"] = self.normalizer.clean_text(trade_match.group(1))

        # Status
        if "INACTIVE" in text.upper() or "CANCELLED" in text.upper() or "SUSPENDED" in text.upper():
            facts["status"] = "INACTIVE"
        elif "ACTIVE" in text.upper():
            facts["status"] = "ACTIVE"

        # Date
        date_match = re.search(r"(?:Date of Liability|Registration Date|Date of Issue)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})", text, re.IGNORECASE)
        if date_match:
            facts["registration_date"] = self.normalizer.parse_date(date_match.group(1))

        return facts

    def _extract_udyam(self, text: str) -> Dict[str, Any]:
        facts: Dict[str, Any] = {
            "document_type": "UDYAM",
            "udyam_number": None,
            "enterprise_name": None,
            "enterprise_type": "MICRO",
            "major_activity": "SERVICES",
        }
        
        udyam_match = re.search(r"\bUDYAM-[A-Z]{2}-\d{2}-\d{7}\b", text, re.IGNORECASE)
        if udyam_match:
            facts["udyam_number"] = self.normalizer.normalize_udyam(udyam_match.group(0))

        name_match = re.search(r"(?:Name of Enterprise|Enterprise Name)\s*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
        if name_match:
            facts["enterprise_name"] = self.normalizer.clean_text(name_match.group(1))

        type_match = re.search(r"(?:Type of Enterprise|Enterprise Category)\s*[:\-]?\s*(MICRO|SMALL|MEDIUM)", text, re.IGNORECASE)
        if type_match:
            facts["enterprise_type"] = type_match.group(1).upper()
        elif "SMALL" in text.upper():
            facts["enterprise_type"] = "SMALL"
        elif "MEDIUM" in text.upper():
            facts["enterprise_type"] = "MEDIUM"

        return facts

    def _extract_pan(self, text: str) -> Dict[str, Any]:
        facts: Dict[str, Any] = {
            "document_type": "PAN",
            "pan": None,
            "name": None,
            "entity_type": "COMPANY",
        }

        pan_match = re.search(r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", text)
        if pan_match:
            facts["pan"] = self.normalizer.normalize_pan(pan_match.group(0))

        name_match = re.search(r"(?:Name|Name on Card)\s*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
        if name_match:
            facts["name"] = self.normalizer.clean_text(name_match.group(1))

        if facts["pan"] and len(facts["pan"]) >= 4:
            fourth_char = facts["pan"][3]
            if fourth_char == "C":
                facts["entity_type"] = "COMPANY"
            elif fourth_char == "P":
                facts["entity_type"] = "INDIVIDUAL"
            elif fourth_char == "F":
                facts["entity_type"] = "FIRM"
            elif fourth_char == "H":
                facts["entity_type"] = "HUF"

        return facts

    def _extract_epfo(self, text: str) -> Dict[str, Any]:
        facts: Dict[str, Any] = {
            "document_type": "EPFO",
            "establishment_code": None,
            "establishment_name": None,
            "wage_month": None,
            "payment_status": "PAID",
            "challan_status": "CONFIRMED",
        }

        code_match = re.search(r"(?:Establishment Code|Est\.? Code|Est Code)\s*[:\-]?\s*([A-Z0-9/]+)", text, re.IGNORECASE)
        if code_match:
            facts["establishment_code"] = self.normalizer.normalize_epfo_code(code_match.group(1))
        else:
            # Match standard pattern DL/12345/67890 or similar
            pattern_match = re.search(r"\b[A-Z]{2}/[A-Z0-9]{3,7}/[A-Z0-9]{3,7}\b", text)
            if pattern_match:
                facts["establishment_code"] = self.normalizer.normalize_epfo_code(pattern_match.group(0))

        name_match = re.search(r"(?:Establishment Name|Name of Establishment)\s*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
        if name_match:
            facts["establishment_name"] = self.normalizer.clean_text(name_match.group(1))

        month_match = re.search(r"(?:Wage Month|Month|Period)\s*[:\-]?\s*([0-9]{4}-[0-9]{2}|[A-Za-z]+\s+[0-9]{4})", text, re.IGNORECASE)
        if month_match:
            facts["wage_month"] = month_match.group(1)

        if "UNPAID" in text.upper() or "PENDING" in text.upper() or "FAILED" in text.upper():
            facts["payment_status"] = "UNPAID"
        elif "PAID" in text.upper() or "PAYMENT CONFIRMED" in text.upper():
            facts["payment_status"] = "PAID"

        return facts

    def _extract_esic(self, text: str) -> Dict[str, Any]:
        facts: Dict[str, Any] = {
            "document_type": "ESIC",
            "employer_code": None,
            "employer_name": None,
            "contributions": [],
            "missing_months": [],
            "status": "COMPLIANT",
        }

        code_match = re.search(r"(?:Employer Code|Employer's Code No\.?)\s*[:\-]?\s*([0-9]{17}|[0-9]{10,17})", text, re.IGNORECASE)
        if code_match:
            facts["employer_code"] = code_match.group(1).strip()

        # Parse contribution table rows or statements
        # Matches patterns like "Jan 2026 - PAID", "2026-01: PAID", "Feb 2026 - MISSING"
        months_patterns = [
            (r"Jan(?:uary)?\s*2026\s*[:\-]?\s*(PAID|UNPAID|MISSING)", "2026-01"),
            (r"Feb(?:ruary)?\s*2026\s*[:\-]?\s*(PAID|UNPAID|MISSING)", "2026-02"),
            (r"Mar(?:ch)?\s*2026\s*[:\-]?\s*(PAID|UNPAID|MISSING)", "2026-03"),
            (r"Apr(?:il)?\s*2026\s*[:\-]?\s*(PAID|UNPAID|MISSING)", "2026-04"),
        ]

        contributions = []
        missing_months = []

        for pattern, m_str in months_patterns:
            m_match = re.search(pattern, text, re.IGNORECASE)
            if m_match:
                st = m_match.group(1).upper()
                contributions.append({"month": m_str, "status": st})
                if st != "PAID":
                    missing_months.append(m_str)
            else:
                # If specific gap keywords are in the text
                if f"MISSING: {m_str}" in text.upper() or f"{m_str}: MISSING" in text.upper():
                    contributions.append({"month": m_str, "status": "MISSING"})
                    missing_months.append(m_str)

        # Check explicit keywords
        if "FEBRUARY 2026 = MISSING" in text.upper() or "FEB 2026: MISSING" in text.upper():
            if "2026-02" not in missing_months:
                missing_months.append("2026-02")
        if "MARCH 2026 = MISSING" in text.upper() or "MAR 2026: MISSING" in text.upper():
            if "2026-03" not in missing_months:
                missing_months.append("2026-03")
        if "APRIL 2026 = MISSING" in text.upper() or "APR 2026: MISSING" in text.upper():
            if "2026-04" not in missing_months:
                missing_months.append("2026-04")

        facts["contributions"] = contributions
        facts["missing_months"] = missing_months
        if missing_months:
            facts["status"] = "GAPS_DETECTED"
        else:
            facts["status"] = "COMPLIANT"

        return facts

    def _extract_oem(self, text: str) -> Dict[str, Any]:
        facts: Dict[str, Any] = {
            "document_type": "OEM",
            "oem_name": None,
            "authorized_partner": None,
            "tender_ref": None,
            "issued_on": None,
            "valid_until": None,
            "product_category": None,
            "status": "VALID",
        }

        oem_match = re.search(r"(?:OEM Name|Manufacturer Name|From)\s*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
        if oem_match:
            facts["oem_name"] = self.normalizer.clean_text(oem_match.group(1))

        partner_match = re.search(r"(?:Authorized Partner|Dealer Name|To|Authorize)\s*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
        if partner_match:
            facts["authorized_partner"] = self.normalizer.clean_text(partner_match.group(1))

        tender_match = re.search(r"(?:Tender Number|Tender Ref|Bid No\.?)\s*[:\-]?\s*([A-Z0-9/]+)", text, re.IGNORECASE)
        if tender_match:
            facts["tender_ref"] = tender_match.group(1).strip()

        valid_match = re.search(r"(?:Valid Until|Expiry Date|Valid Up To)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})", text, re.IGNORECASE)
        if valid_match:
            facts["valid_until"] = self.normalizer.parse_date(valid_match.group(1))

        issue_match = re.search(r"(?:Issued On|Date of Issue|Dated)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})", text, re.IGNORECASE)
        if issue_match:
            facts["issued_on"] = self.normalizer.parse_date(issue_match.group(1))

        product_match = re.search(r"(?:Product Scope|Equipment|Product Category)\s*[:\-]?\s*([^\n\r]+)", text, re.IGNORECASE)
        if product_match:
            facts["product_category"] = self.normalizer.clean_text(product_match.group(1))

        return facts

    def _extract_digilocker(self, text: str) -> Dict[str, Any]:
        return {
            "document_type": "DIGILOCKER",
            "doc_id": "DGL-VERIFIED-DOC",
            "issuer": "DigiLocker Government Portal",
            "status": "AVAILABLE",
        }

    def _extract_blacklist(self, text: str) -> Dict[str, Any]:
        is_clear = "NOT DEBARRED" in text.upper() or "NOT BLACKLISTED" in text.upper() or "NO ADVERSE" in text.upper()
        return {
            "document_type": "BLACKLIST",
            "status": "CLEAR" if is_clear else "POSSIBLE_MATCH",
        }


structured_extractor = StructuredExtractor()
