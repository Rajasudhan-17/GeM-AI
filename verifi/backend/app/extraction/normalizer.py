import re
from datetime import datetime
from typing import Optional


class TextNormalizer:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def normalize_gstin(gstin: Optional[str]) -> Optional[str]:
        if not gstin:
            return None
        cleaned = re.sub(r"[^A-Z0-9]", "", gstin.upper())
        return cleaned if len(cleaned) == 15 else cleaned

    @staticmethod
    def normalize_pan(pan: Optional[str]) -> Optional[str]:
        if not pan:
            return None
        cleaned = re.sub(r"[^A-Z0-9]", "", pan.upper())
        return cleaned if len(cleaned) == 10 else cleaned

    @staticmethod
    def normalize_udyam(udyam: Optional[str]) -> Optional[str]:
        if not udyam:
            return None
        cleaned = udyam.upper().strip()
        # Normal format: UDYAM-XX-00-0000000
        return cleaned

    @staticmethod
    def normalize_epfo_code(code: Optional[str]) -> Optional[str]:
        if not code:
            return None
        return code.upper().strip()

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[str]:
        """Attempts to parse standard date formats to YYYY-MM-DD."""
        if not date_str:
            return None
        date_str = date_str.strip()
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d %b %Y",
            "%d %B %Y",
            "%Y/%m/%d",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str
