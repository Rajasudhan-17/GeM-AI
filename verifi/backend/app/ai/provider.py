from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class AIProvider(ABC):
    @abstractmethod
    async def generate_explanation(
        self,
        bidder_name: str,
        score: float,
        risk_level: str,
        checks: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def answer_chat(
        self,
        message: str,
        bidder_name: str,
        score: float,
        risk_level: str,
        checks: List[Dict[str, Any]],
        focus_check_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def draft_decision_reason(
        self,
        bidder_name: str,
        score: float,
        risk_level: str,
        checks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        pass


class MockAIProvider(AIProvider):
    async def generate_explanation(
        self,
        bidder_name: str,
        score: float,
        risk_level: str,
        checks: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        failed = [c for c in checks if c.get("status") == "FAIL"]
        review = [c for c in checks if c.get("status") == "REVIEW"]
        passed = [c for c in checks if c.get("status") == "PASS"]

        findings = []
        for c in failed:
            findings.append(f"FAILED: {c.get('check_name')} – {c.get('reason')}")
        for c in review:
            findings.append(f"REVIEW: {c.get('check_name')} – {c.get('reason')}")

        if not failed and not review:
            summary = f"All {len(passed)} statutory and technical requirements for {bidder_name} are fully compliant and verified against authoritative government sources. Zero discrepancies detected."
            risk_exp = f"Risk is assessed as {risk_level} ({score}/100) due to 100% verified compliance across GST, PAN, Udyam, EPFO, ESIC, and OEM credentials."
            suggested_action = "ACCEPT"
            drafted_reason = f"Bidder {bidder_name} demonstrated full compliance with all tender mandatory qualifications and statutory registrations with a verified score of {score}%."
        elif failed:
            issues = "; ".join([f"{c.get('check_name')}: {c.get('reason')}" for c in failed])
            summary = f"Identified {len(failed)} critical compliance failure(s) for {bidder_name}. Primary non-compliance: {issues}."
            risk_exp = f"Risk elevated to {risk_level} ({score}/100) due to statutory discrepancies and/or unverified eligibility."
            suggested_action = "REJECT"
            drafted_reason = f"Disqualified due to non-compliance in mandatory criteria: {issues}. Final compliance score: {score}% ({risk_level} Risk)."
        else:
            issues = "; ".join([f"{c.get('check_name')}: {c.get('reason')}" for c in review])
            summary = f"Bidder {bidder_name} meets primary criteria with score {score}%, but {len(review)} item(s) require officer verification: {issues}."
            risk_exp = f"Risk is classified as {risk_level} ({score}/100). Technical flags are present but do not constitute disqualification."
            suggested_action = "FURTHER_INSPECTION"
            drafted_reason = f"Qualified subject to verification of pending review items ({issues}). Compliance score: {score}%."

        return {
            "summary": summary,
            "risk_explanation": risk_exp,
            "key_findings": findings,
            "suggested_action": suggested_action,
            "drafted_reason": drafted_reason,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def answer_chat(
        self,
        message: str,
        bidder_name: str,
        score: float,
        risk_level: str,
        checks: List[Dict[str, Any]],
        focus_check_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        msg_lower = message.lower()
        related_checks = []

        # Find focused or matching check
        gst_check = next((c for c in checks if c.get("rule_code") == "GST-001"), None)
        esic_check = next((c for c in checks if c.get("rule_code") == "ESIC-001"), None)
        oem_check = next((c for c in checks if c.get("rule_code") == "OEM-001"), None)
        pan_check = next((c for c in checks if c.get("rule_code") == "PAN-001"), None)
        bl_check = next((c for c in checks if c.get("rule_code") == "BL-001"), None)

        if "gst" in msg_lower:
            related_checks.append("GST-001")
            if gst_check:
                comp = gst_check.get("fact_comparison", {}).get("field_comparisons", {}).get("gstin", {})
                doc_g = comp.get("document", "N/A")
                src_g = comp.get("source", "N/A")
                st = gst_check.get("status")
                if st == "FAIL":
                    answer = f"The GST check is flagged as FAIL because the submitted document GSTIN ({doc_g}) does not match the authoritative GST portal record ({src_g}). Under GeM rule GST-001, a mismatch between submitted credentials and government databases constitutes a compliance failure."
                else:
                    answer = f"The GST registration for {bidder_name} is verified and ACTIVE with GSTIN {doc_g}."
            else:
                answer = "GST check data is not available for this bidder."

        elif "esic" in msg_lower or "esi" in msg_lower:
            related_checks.append("ESIC-001")
            if esic_check:
                st = esic_check.get("status")
                reason = esic_check.get("reason", "")
                if st != "PASS":
                    answer = f"The ESIC verification failed/flagged because {reason} Statutory compliance requires continuous un-interrupted contribution returns for all active employees."
                else:
                    answer = f"ESIC contribution records are completely paid and verified with no missing months."
            else:
                answer = "ESIC check data is not available."

        elif "oem" in msg_lower or "maf" in msg_lower or "authorization" in msg_lower or "expiry" in msg_lower:
            related_checks.append("OEM-001")
            if oem_check:
                st = oem_check.get("status")
                reason = oem_check.get("reason", "")
                if st == "REVIEW":
                    answer = f"The OEM Authorization is flagged for REVIEW because {reason} The document is authentic and currently valid, but approaching its expiration window within the delivery schedule. Officer discretion is advised."
                elif st == "FAIL":
                    answer = f"The OEM Authorization is marked FAIL because {reason}"
                else:
                    answer = f"The OEM Authorization letter is valid, authentic, and covers the required networking equipment."
            else:
                answer = "OEM check data is not available."

        elif "low risk" in msg_lower or "why is this bidder low risk" in msg_lower:
            related_checks = [c.get("rule_code") for c in checks if c.get("status") == "PASS"]
            answer = f"{bidder_name} is classified as LOW RISK ({score}/100) because all core statutory verifications (GST, PAN, EPFO, ESIC, Udyam) and OEM technical credentials passed authoritative government cross-checks with zero integrity violations or active debarments."

        elif "high risk" in msg_lower or "why is this bidder high risk" in msg_lower:
            failed_codes = [c.get("rule_code") for c in checks if c.get("status") == "FAIL"]
            related_checks = failed_codes
            answer = f"{bidder_name} is classified as HIGH RISK ({score}/100) due to multiple critical failures: {', '.join(failed_codes)}. These include statutory inconsistencies, unverified eligibility, or central debarment."

        elif "decision" in msg_lower or "recommend" in msg_lower or "reject" in msg_lower or "accept" in msg_lower:
            failed_count = sum(1 for c in checks if c.get("status") == "FAIL")
            if failed_count > 0:
                answer = f"Based on {failed_count} critical compliance failure(s) (including {', '.join([c.get('rule_code') for c in checks if c.get('status') == 'FAIL'])}), the recommended procurement decision is REJECT. The evaluation officer should review the drafted justification before final submission."
            else:
                answer = f"With a compliance score of {score}% and no critical failures, the recommendation is ACCEPT."

        else:
            # General answer
            failed_count = sum(1 for c in checks if c.get("status") == "FAIL")
            review_count = sum(1 for c in checks if c.get("status") == "REVIEW")
            answer = f"For bidder {bidder_name}, verification achieved an overall compliance score of {score}% ({risk_level} Risk). There are {failed_count} failed checks and {review_count} checks requiring officer review."

        return {
            "answer": answer,
            "related_checks": related_checks,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def draft_decision_reason(
        self,
        bidder_name: str,
        score: float,
        risk_level: str,
        checks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        failed = [c for c in checks if c.get("status") == "FAIL"]
        review = [c for c in checks if c.get("status") == "REVIEW"]

        if failed:
            details = "; ".join([f"{c.get('check_name')} ({c.get('rule_code')}): {c.get('reason')}" for c in failed])
            reason = (
                f"The bid submitted by {bidder_name} is REJECTED due to failure in fulfilling mandatory eligibility "
                f"criteria. Discrepancies detected: {details}. Overall compliance score: {score}% ({risk_level} Risk). "
                f"In accordance with GeM procurement guidelines, bids with mismatched statutory credentials or debarment cannot be accepted."
            )
            suggested = "REJECTED"
        elif review:
            details = "; ".join([f"{c.get('check_name')}: {c.get('reason')}" for c in review])
            reason = (
                f"The bid submitted by {bidder_name} is ACCEPTED subject to satisfactory submission of undertakings "
                f"for the following review items: {details}. Final technical score: {score}% ({risk_level} Risk)."
            )
            suggested = "ACCEPTED"
        else:
            reason = (
                f"The bid submitted by {bidder_name} is ACCEPTED. All statutory documents (GST, PAN, EPFO, ESIC, Udyam) "
                f"and technical OEM credentials have been verified against authoritative government databases with "
                f"a verified compliance score of {score}% ({risk_level} Risk)."
            )
            suggested = "ACCEPTED"

        return {
            "reason": reason,
            "suggested_decision": suggested,
            "confidence": 0.95,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


mock_ai_provider = MockAIProvider()
