import re
from typing import Optional
from app.core.enums import DocumentType


class DocumentClassifier:
    # Deterministic regex patterns
    GST_PATTERN = re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b", re.IGNORECASE)
    UDYAM_PATTERN = re.compile(r"\bUDYAM-[A-Z]{2}-\d{2}-\d{7}\b", re.IGNORECASE)
    PAN_PATTERN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", re.IGNORECASE)
    
    def classify(self, text: str, filename_hint: Optional[str] = None) -> DocumentType:
        if not text:
            if filename_hint:
                return self._classify_by_filename(filename_hint)
            return DocumentType.UNKNOWN

        text_upper = text.upper()

        # 1. GST check
        if "GOODS AND SERVICES TAX" in text_upper or "GSTIN" in text_upper or "FORM GST REG-06" in text_upper:
            return DocumentType.GST
        if self.GST_PATTERN.search(text_upper) and "TAX INVOICE" not in text_upper:
            return DocumentType.GST

        # 2. Udyam check
        if "UDYAM REGISTRATION CERTIFICATE" in text_upper or "MINISTRY OF MICRO, SMALL" in text_upper or self.UDYAM_PATTERN.search(text_upper):
            return DocumentType.UDYAM

        # 3. EPFO check
        if "EMPLOYEES' PROVIDENT FUND" in text_upper or "EPFO" in text_upper or "ESTABLISHMENT CODE" in text_upper or "ELECTRONIC CHALLAN CUM RETURN" in text_upper:
            return DocumentType.EPFO

        # 4. ESIC check
        if "EMPLOYEES' STATE INSURANCE" in text_upper or "ESIC" in text_upper or "MONTHLY CONTRIBUTION" in text_upper:
            return DocumentType.ESIC

        # 5. OEM check
        if "MANUFACTURER'S AUTHORIZATION" in text_upper or "OEM AUTHORIZATION" in text_upper or "AUTHORIZATION LETTER" in text_upper or "AUTHORIZED DEALER" in text_upper or "ORIGINAL EQUIPMENT MANUFACTURER" in text_upper:
            return DocumentType.OEM

        # 6. PAN check
        if "INCOME TAX DEPARTMENT" in text_upper or "PERMANENT ACCOUNT NUMBER" in text_upper:
            return DocumentType.PAN
        if self.PAN_PATTERN.search(text_upper) and ("PAN" in text_upper or "FATHER'S NAME" in text_upper):
            return DocumentType.PAN

        # 7. DigiLocker check
        if "DIGILOCKER" in text_upper or "DIGITALLY SIGNED CERTIFICATE" in text_upper:
            return DocumentType.DIGILOCKER

        # 8. Blacklist / Debarment check
        if "DEBARMENT" in text_upper or "BLACKLIST" in text_upper or "NON-DEBARMENT DECLARATION" in text_upper:
            return DocumentType.BLACKLIST

        # Fallback to filename hint if content is ambiguous
        if filename_hint:
            return self._classify_by_filename(filename_hint)

        return DocumentType.UNKNOWN

    def _classify_by_filename(self, filename: str) -> DocumentType:
        fn = filename.lower()
        if "gst" in fn:
            return DocumentType.GST
        if "udyam" in fn or "msme" in fn:
            return DocumentType.UDYAM
        if "pan" in fn:
            return DocumentType.PAN
        if "epfo" in fn or "pf" in fn or "provident" in fn:
            return DocumentType.EPFO
        if "esic" in fn or "esi" in fn:
            return DocumentType.ESIC
        if "oem" in fn or "maf" in fn or "auth" in fn:
            return DocumentType.OEM
        if "digilocker" in fn:
            return DocumentType.DIGILOCKER
        if "blacklist" in fn or "debar" in fn:
            return DocumentType.BLACKLIST
        return DocumentType.UNKNOWN


classifier = DocumentClassifier()
