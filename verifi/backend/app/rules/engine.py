import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.core.enums import VerificationStatus, DocumentType
from app.models.verification import VerificationCheck, FactComparison
from app.rules.definitions import RULE_DEFINITIONS, RuleDefinition
from app.rules.evaluator import RuleEvaluator
from app.providers.base import ProviderVerificationResult


class RuleEngine:
    def __init__(self):
        self.evaluator = RuleEvaluator()

    def evaluate(
        self,
        run_id: str,
        requirement_code: str,
        rule_code: str,
        check_name: str,
        document_type: DocumentType,
        document_id: Optional[str],
        doc_facts: Optional[Dict[str, Any]],
        provider_result: Optional[ProviderVerificationResult],
    ) -> VerificationCheck:
        rule_def = RULE_DEFINITIONS.get(rule_code)
        
        is_available = provider_result.is_available if provider_result else True
        auth_facts = provider_result.authoritative_facts if provider_result else {}

        # Route to deterministic evaluator
        if rule_code == "GST-001":
            status, reason, comparisons = self.evaluator.evaluate_gst(doc_facts, auth_facts, is_available)
        elif rule_code == "UDYAM-001":
            status, reason, comparisons = self.evaluator.evaluate_udyam(doc_facts, auth_facts, is_available)
        elif rule_code == "PAN-001":
            status, reason, comparisons = self.evaluator.evaluate_pan(doc_facts, auth_facts, is_available)
        elif rule_code == "EPFO-001":
            status, reason, comparisons = self.evaluator.evaluate_epfo(doc_facts, auth_facts, is_available)
        elif rule_code == "ESIC-001":
            status, reason, comparisons = self.evaluator.evaluate_esic(doc_facts, auth_facts, is_available)
        elif rule_code == "OEM-001":
            status, reason, comparisons = self.evaluator.evaluate_oem(doc_facts, auth_facts, is_available)
        elif rule_code == "DGL-001":
            status, reason, comparisons = self.evaluator.evaluate_digilocker(doc_facts, auth_facts, is_available)
        elif rule_code == "BL-001":
            status, reason, comparisons = self.evaluator.evaluate_blacklist(doc_facts, auth_facts, is_available)
        else:
            status = VerificationStatus.REVIEW
            reason = f"Unknown rule code '{rule_code}'. Routed for manual evaluation."
            comparisons = {}

        # Discrepancies
        discrepancies = []
        for field, comp in comparisons.items():
            if comp.get("matched") is False:
                discrepancies.append(f"Mismatch in {field}: document={comp.get('document')}, source={comp.get('source')}")

        fact_comparison = FactComparison(
            matched=(status == VerificationStatus.PASS),
            discrepancies=discrepancies,
            field_comparisons=comparisons,
        )

        return VerificationCheck(
            id=f"CHK-{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            requirement_code=requirement_code,
            rule_code=rule_code,
            check_name=check_name,
            document_type=document_type,
            document_id=document_id,
            status=status,
            extracted_facts=doc_facts or {},
            source_facts=auth_facts or {},
            fact_comparison=fact_comparison,
            reason=reason,
            evidence={
                "rule_weight": rule_def.weight if rule_def else 10.0,
                "provider": provider_result.source_name if provider_result else "INTERNAL",
                "provider_available": is_available,
            },
            evaluated_at=datetime.now(timezone.utc),
        )


rule_engine = RuleEngine()
