from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.core.enums import DocumentType


@dataclass(frozen=True)
class RuleDefinition:
    rule_code: str
    name: str
    document_type: DocumentType
    weight: float
    description: str
    failure_message: str
    review_message: str
    pass_message: str


RULE_DEFINITIONS: Dict[str, RuleDefinition] = {
    "GST-001": RuleDefinition(
        rule_code="GST-001",
        name="GSTIN Authenticity and Active Registration Rule",
        document_type=DocumentType.GST,
        weight=15.0,
        description="Verifies that submitted document GSTIN matches authoritative GST portal record and registration status is ACTIVE.",
        failure_message="Submitted GSTIN does not match authoritative GST record or registration status is cancelled/inactive.",
        review_message="GST verification requires manual review due to data discrepancies or source provider downtime.",
        pass_message="Submitted GSTIN matches authoritative GST record and registration is ACTIVE.",
    ),
    "UDYAM-001": RuleDefinition(
        rule_code="UDYAM-001",
        name="MSME Udyam Registration Validity Rule",
        document_type=DocumentType.UDYAM,
        weight=10.0,
        description="Verifies Udyam registration number authenticity with MSME portal and confirms valid classification.",
        failure_message="Udyam registration is invalid or not found in MSME portal.",
        review_message="Udyam certificate details require manual officer verification.",
        pass_message="Udyam registration number verified and active on MSME portal.",
    ),
    "PAN-001": RuleDefinition(
        rule_code="PAN-001",
        name="Income Tax PAN Validity and Entity Matching Rule",
        document_type=DocumentType.PAN,
        weight=15.0,
        description="Verifies PAN card against Income Tax department records and matches entity name.",
        failure_message="Submitted PAN does not match authoritative Income Tax records or entity mismatch detected.",
        review_message="PAN details require manual verification due to minor name differences.",
        pass_message="PAN verified as valid and active with matching entity identity.",
    ),
    "EPFO-001": RuleDefinition(
        rule_code="EPFO-001",
        name="EPFO Establishment Code and Active Remittance Rule",
        document_type=DocumentType.EPFO,
        weight=10.0,
        description="Verifies EPFO establishment code and recent electronic challan remittance status.",
        failure_message="EPFO establishment code missing or account is in default/inactive status.",
        review_message="EPFO payment status requires confirmation with latest challan submission.",
        pass_message="EPFO establishment code verified with confirmed active remittance.",
    ),
    "ESIC-001": RuleDefinition(
        rule_code="ESIC-001",
        name="ESIC Contribution Compliance and Gap Detection Rule",
        document_type=DocumentType.ESIC,
        weight=10.0,
        description="Verifies employer ESIC registration and checks for contribution gaps in required months.",
        failure_message="ESIC contributions contain critical missing payment periods or account is suspended.",
        review_message="ESIC contributions show payment gaps requiring clarification or proof of exemption.",
        pass_message="ESIC monthly contributions are fully paid and compliant.",
    ),
    "OEM-001": RuleDefinition(
        rule_code="OEM-001",
        name="OEM Manufacturer Authorization and Expiry Rule",
        document_type=DocumentType.OEM,
        weight=15.0,
        description="Verifies OEM Manufacturer Authorization Form (MAF) validity, tender reference, and expiry date.",
        failure_message="OEM authorization is invalid, expired, or does not cover required product scope.",
        review_message="OEM authorization is valid but approaching expiry within 30 days or requires clarification.",
        pass_message="OEM authorization is active, valid for tender, and covers full product scope.",
    ),
    "DGL-001": RuleDefinition(
        rule_code="DGL-001",
        name="DigiLocker Digital Signature and Tamper Verification Rule",
        document_type=DocumentType.DIGILOCKER,
        weight=10.0,
        description="Verifies document digital signatures and issuer authenticity via DigiLocker gateway.",
        failure_message="Digital signature validation failed or certificate has been tampered with.",
        review_message="DigiLocker verification gateway is temporarily unavailable. Document routed for manual review.",
        pass_message="Document issuer digitally verified and tamper-proof via DigiLocker.",
    ),
    "BL-001": RuleDefinition(
        rule_code="BL-001",
        name="Debarment and Central Blacklist Exclusion Rule",
        document_type=DocumentType.BLACKLIST,
        weight=15.0,
        description="Verifies bidder against Central Debarment / GeM Blacklist database.",
        failure_message="Bidder is currently DEBARRED / BLACKLISTED from government procurement.",
        review_message="Potential name match found on watch list requiring legal clearance.",
        pass_message="Bidder is clear with no active debarment or blacklist records.",
    ),
}
