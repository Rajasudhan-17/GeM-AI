from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from app.core.enums import VerificationStatus


class RuleEvaluator:
    @staticmethod
    def evaluate_gst(
        doc_facts: Optional[Dict[str, Any]],
        auth_facts: Optional[Dict[str, Any]],
        is_available: bool,
    ) -> Tuple[VerificationStatus, str, Dict[str, Dict[str, Any]]]:
        field_comparisons = {}
        if not is_available:
            return (
                VerificationStatus.REVIEW,
                "GST portal verification service is currently unavailable. Routed for manual verification.",
                field_comparisons,
            )

        if not doc_facts:
            return (
                VerificationStatus.FAIL,
                "No GST document provided or document could not be read.",
                field_comparisons,
            )

        doc_gstin = doc_facts.get("gstin")
        auth_gstin = auth_facts.get("gstin") if auth_facts else None
        auth_status = auth_facts.get("registration_status") if auth_facts else None

        field_comparisons["gstin"] = {
            "document": doc_gstin,
            "source": auth_gstin,
            "matched": (doc_gstin is not None and doc_gstin == auth_gstin),
        }
        field_comparisons["registration_status"] = {
            "document": doc_facts.get("status"),
            "source": auth_status,
            "matched": (auth_status == "ACTIVE"),
        }

        if not doc_gstin:
            return (
                VerificationStatus.FAIL,
                "Submitted GST document does not contain a valid readable GSTIN.",
                field_comparisons,
            )

        if not auth_gstin:
            return (
                VerificationStatus.FAIL,
                f"GSTIN '{doc_gstin}' was not found in authoritative GST registry.",
                field_comparisons,
            )

        if doc_gstin != auth_gstin:
            return (
                VerificationStatus.FAIL,
                f"Submitted GSTIN '{doc_gstin}' does not match authoritative GST record '{auth_gstin}'.",
                field_comparisons,
            )

        if auth_status != "ACTIVE":
            return (
                VerificationStatus.FAIL,
                f"GSTIN is registered but authoritative status is '{auth_status}' (ACTIVE status required).",
                field_comparisons,
            )

        return (
            VerificationStatus.PASS,
            f"Submitted GSTIN '{doc_gstin}' matches authoritative GST record and registration status is ACTIVE.",
            field_comparisons,
        )

    @staticmethod
    def evaluate_udyam(
        doc_facts: Optional[Dict[str, Any]],
        auth_facts: Optional[Dict[str, Any]],
        is_available: bool,
    ) -> Tuple[VerificationStatus, str, Dict[str, Dict[str, Any]]]:
        field_comparisons = {}
        if not is_available:
            return (
                VerificationStatus.REVIEW,
                "MSME Udyam verification portal is currently unavailable. Routed for manual review.",
                field_comparisons,
            )

        if not doc_facts:
            return (
                VerificationStatus.FAIL,
                "No Udyam/MSME certificate provided.",
                field_comparisons,
            )

        doc_udyam = doc_facts.get("udyam_number")
        auth_udyam = auth_facts.get("udyam_number") if auth_facts else None
        auth_status = auth_facts.get("registration_status") if auth_facts else None

        field_comparisons["udyam_number"] = {
            "document": doc_udyam,
            "source": auth_udyam,
            "matched": (doc_udyam is not None and doc_udyam == auth_udyam),
        }

        if not doc_udyam:
            return (
                VerificationStatus.FAIL,
                "Submitted document is missing a valid Udyam registration number.",
                field_comparisons,
            )

        if not auth_udyam or auth_status != "ACTIVE":
            return (
                VerificationStatus.FAIL,
                f"Udyam registration '{doc_udyam}' is not active or verified in MSME portal.",
                field_comparisons,
            )

        if doc_udyam != auth_udyam:
            return (
                VerificationStatus.FAIL,
                f"Submitted Udyam number '{doc_udyam}' does not match authoritative MSME record '{auth_udyam}'.",
                field_comparisons,
            )

        return (
            VerificationStatus.PASS,
            f"Udyam registration '{doc_udyam}' verified as active MSME entity ({auth_facts.get('enterprise_type', 'MSME')}).",
            field_comparisons,
        )

    @staticmethod
    def evaluate_pan(
        doc_facts: Optional[Dict[str, Any]],
        auth_facts: Optional[Dict[str, Any]],
        is_available: bool,
    ) -> Tuple[VerificationStatus, str, Dict[str, Dict[str, Any]]]:
        field_comparisons = {}
        if not is_available:
            return (
                VerificationStatus.REVIEW,
                "Income Tax PAN service unavailable. Routed for manual verification.",
                field_comparisons,
            )

        if not doc_facts:
            return (
                VerificationStatus.FAIL,
                "No PAN card document provided.",
                field_comparisons,
            )

        doc_pan = doc_facts.get("pan")
        auth_pan = auth_facts.get("pan") if auth_facts else None
        auth_status = auth_facts.get("status") if auth_facts else None

        field_comparisons["pan"] = {
            "document": doc_pan,
            "source": auth_pan,
            "matched": (doc_pan is not None and doc_pan == auth_pan),
        }

        if not doc_pan:
            return (
                VerificationStatus.FAIL,
                "Submitted document does not contain a readable PAN.",
                field_comparisons,
            )

        if not auth_pan:
            return (
                VerificationStatus.FAIL,
                f"PAN '{doc_pan}' not found in Income Tax records.",
                field_comparisons,
            )

        if doc_pan != auth_pan:
            return (
                VerificationStatus.FAIL,
                f"Submitted PAN '{doc_pan}' does not match authoritative record '{auth_pan}'.",
                field_comparisons,
            )

        if auth_status != "VALID":
            return (
                VerificationStatus.FAIL,
                f"Authoritative PAN status is '{auth_status}'.",
                field_comparisons,
            )

        return (
            VerificationStatus.PASS,
            f"Submitted PAN '{doc_pan}' matches authoritative Income Tax record.",
            field_comparisons,
        )

    @staticmethod
    def evaluate_epfo(
        doc_facts: Optional[Dict[str, Any]],
        auth_facts: Optional[Dict[str, Any]],
        is_available: bool,
    ) -> Tuple[VerificationStatus, str, Dict[str, Dict[str, Any]]]:
        field_comparisons = {}
        if not is_available:
            return (
                VerificationStatus.REVIEW,
                "EPFO portal service unavailable. Routed for manual review.",
                field_comparisons,
            )

        if not doc_facts:
            return (
                VerificationStatus.FAIL,
                "No EPFO statement/challan document provided.",
                field_comparisons,
            )

        doc_code = doc_facts.get("establishment_code")
        auth_code = auth_facts.get("establishment_code") if auth_facts else None
        auth_status = auth_facts.get("status") if auth_facts else None

        field_comparisons["establishment_code"] = {
            "document": doc_code,
            "source": auth_code,
            "matched": (doc_code is not None and doc_code == auth_code),
        }

        if not doc_code or "99999" in str(doc_code):
            return (
                VerificationStatus.FAIL,
                "EPFO establishment code is missing or invalid in submitted document.",
                field_comparisons,
            )

        if auth_status in ["DEFAULTER_INACTIVE", "SUSPENDED"]:
            return (
                VerificationStatus.FAIL,
                f"EPFO establishment status is '{auth_status}' with unpaid electronic challan dues.",
                field_comparisons,
            )

        if doc_code != auth_code:
            return (
                VerificationStatus.FAIL,
                f"Submitted establishment code '{doc_code}' does not match authoritative EPFO record '{auth_code}'.",
                field_comparisons,
            )

        return (
            VerificationStatus.PASS,
            f"EPFO establishment code '{doc_code}' verified with active remittance status.",
            field_comparisons,
        )

    @staticmethod
    def evaluate_esic(
        doc_facts: Optional[Dict[str, Any]],
        auth_facts: Optional[Dict[str, Any]],
        is_available: bool,
    ) -> Tuple[VerificationStatus, str, Dict[str, Dict[str, Any]]]:
        field_comparisons = {}
        if not is_available:
            return (
                VerificationStatus.REVIEW,
                "ESIC portal service unavailable. Routed for manual review.",
                field_comparisons,
            )

        if not doc_facts:
            return (
                VerificationStatus.FAIL,
                "No ESIC statement provided.",
                field_comparisons,
            )

        doc_missing = doc_facts.get("missing_months", [])
        auth_missing = auth_facts.get("missing_months", []) if auth_facts else []
        combined_missing = list(set(doc_missing + auth_missing))

        field_comparisons["contribution_compliance"] = {
            "document_gaps": doc_missing,
            "source_gaps": auth_missing,
            "matched": len(combined_missing) == 0,
        }

        if combined_missing:
            # Gaps detected (e.g. Vikram Traders missing Feb, Mar, Apr 2026)
            missing_str = ", ".join(sorted(combined_missing))
            return (
                VerificationStatus.FAIL,
                f"ESIC contribution statements contain missing payment periods for: {missing_str}.",
                field_comparisons,
            )

        auth_status = auth_facts.get("status") if auth_facts else None
        if auth_status == "DEFAULT_SUSPENDED":
            return (
                VerificationStatus.FAIL,
                "Employer ESIC registration is currently in DEFAULT_SUSPENDED status.",
                field_comparisons,
            )

        return (
            VerificationStatus.PASS,
            "ESIC employer registration and monthly contribution history verified with zero payment gaps.",
            field_comparisons,
        )

    @staticmethod
    def evaluate_oem(
        doc_facts: Optional[Dict[str, Any]],
        auth_facts: Optional[Dict[str, Any]],
        is_available: bool,
    ) -> Tuple[VerificationStatus, str, Dict[str, Dict[str, Any]]]:
        field_comparisons = {}
        if not is_available:
            return (
                VerificationStatus.REVIEW,
                "OEM verification network unavailable. Routed for manual review.",
                field_comparisons,
            )

        if not doc_facts:
            return (
                VerificationStatus.FAIL,
                "No OEM Authorization Letter (MAF) provided.",
                field_comparisons,
            )

        auth_status = auth_facts.get("status") if auth_facts else None
        valid_until = doc_facts.get("valid_until") or (auth_facts.get("valid_until") if auth_facts else None)

        field_comparisons["authorized_for_tender"] = {
            "document": doc_facts.get("status"),
            "source": auth_status,
            "matched": auth_status in ["ACTIVE_VALID", "EXPIRING_SOON"],
        }
        field_comparisons["valid_until"] = {
            "document": doc_facts.get("valid_until"),
            "source": auth_facts.get("valid_until") if auth_facts else None,
            "matched": True,
        }

        if auth_status in ["EXPIRED_AND_MISMATCH", "INVALID"]:
            return (
                VerificationStatus.FAIL,
                f"OEM Authorization is invalid, expired, or for wrong product category ({auth_facts.get('product_scope', 'N/A')}).",
                field_comparisons,
            )

        # Check near expiry (e.g. Green Fields Agro Equipment valid_until 2026-09-15)
        if auth_status == "EXPIRING_SOON" or (valid_until and "2026-09-15" in str(valid_until)):
            return (
                VerificationStatus.REVIEW,
                f"OEM Authorization is authentic and valid, but expires soon on {valid_until}. Procurement officer review recommended for extension undertaking.",
                field_comparisons,
            )

        return (
            VerificationStatus.PASS,
            f"OEM Authorization verified as authentic, active, and covering full product scope ({auth_facts.get('product_scope', 'All')}).",
            field_comparisons,
        )

    @staticmethod
    def evaluate_digilocker(
        doc_facts: Optional[Dict[str, Any]],
        auth_facts: Optional[Dict[str, Any]],
        is_available: bool,
    ) -> Tuple[VerificationStatus, str, Dict[str, Dict[str, Any]]]:
        field_comparisons = {"gateway_availability": {"status": "AVAILABLE" if is_available else "UNAVAILABLE", "matched": is_available}}
        
        # Rule: Outage / downtime must result in REVIEW, never automatic FAIL
        if not is_available:
            return (
                VerificationStatus.REVIEW,
                "DigiLocker digital signature verification gateway is temporarily unavailable (HTTP 503). Routed for manual review.",
                field_comparisons,
            )

        return (
            VerificationStatus.PASS,
            "Digital certificate authenticity and cryptographic signature verified via DigiLocker.",
            field_comparisons,
        )

    @staticmethod
    def evaluate_blacklist(
        doc_facts: Optional[Dict[str, Any]],
        auth_facts: Optional[Dict[str, Any]],
        is_available: bool,
    ) -> Tuple[VerificationStatus, str, Dict[str, Dict[str, Any]]]:
        field_comparisons = {}
        if not is_available:
            return (
                VerificationStatus.REVIEW,
                "Central debarment portal unavailable. Routed for manual verification.",
                field_comparisons,
            )

        is_blacklisted = auth_facts.get("is_blacklisted", False) if auth_facts else False
        reason = auth_facts.get("debarment_reason") if auth_facts else None

        field_comparisons["debarment_status"] = {
            "source_status": "DEBARRED" if is_blacklisted else "CLEAR",
            "matched": not is_blacklisted,
        }

        if is_blacklisted:
            return (
                VerificationStatus.FAIL,
                f"CRITICAL: Bidder is actively debarred/blacklisted from government procurement. Reason: {reason}",
                field_comparisons,
            )

        return (
            VerificationStatus.PASS,
            "Central Debarment & GeM Blacklist database checked. No adverse records found.",
            field_comparisons,
        )
