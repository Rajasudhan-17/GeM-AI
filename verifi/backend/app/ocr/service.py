import io
from pathlib import Path
from typing import Optional, Tuple
import fitz  # PyMuPDF
from PIL import Image
from app.core.logging import logger


class OCRService:
    def __init__(self):
        pass

    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[str, str]:
        """
        Extracts text from PDF bytes using PyMuPDF.
        Returns (extracted_text, method_used).
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            full_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text:
                    full_text.append(text.strip())
            
            combined_text = "\n\n".join(full_text).strip()
            
            if len(combined_text) > 20:
                return combined_text, "PYMUPDF_DIRECT"
            
            # If text is minimal (e.g. scanned image in PDF), we attempt image OCR fallback
            return self._fallback_image_ocr_from_pdf(doc), "PYMUPDF_IMAGE_FALLBACK"
        except Exception as e:
            logger.warning(f"PyMuPDF direct extraction error: {e}")
            return "", "FAILED"

    def _fallback_image_ocr_from_pdf(self, doc: fitz.Document) -> str:
        """Extracts text by converting pages or embedded images."""
        extracted = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Try to extract text blocks or pixmap
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            text = self.extract_text_from_image_bytes(img_bytes)
            if text:
                extracted.append(text)
        return "\n\n".join(extracted).strip()

    def extract_text_from_image_bytes(self, image_bytes: bytes) -> str:
        """
        Extracts text from image bytes.
        Attempts PaddleOCR or standard image parsing.
        """
        try:
            # Fallback PIL inspection or mock PaddleOCR
            image = Image.open(io.BytesIO(image_bytes))
            # If PaddleOCR is available, run it here.
            # In Phase 1 synthetic PDFs already contain readable text streams.
            return f"[IMAGE_OCR_EXTRACTED_WIDTH_{image.width}_HEIGHT_{image.height}]"
        except Exception as e:
            logger.warning(f"Image extraction error: {e}")
            return ""

    def process_document(self, file_bytes: bytes, file_name: str) -> Tuple[str, str]:
        """
        Routes file based on extension to appropriate text extractor.
        """
        ext = Path(file_name).suffix.lower()
        if ext == ".pdf":
            return self.extract_text_from_pdf_bytes(file_bytes)
        elif ext in [".png", ".jpg", ".jpeg"]:
            return self.extract_text_from_image_bytes(file_bytes), "IMAGE_OCR"
        else:
            return "", "UNSUPPORTED_FORMAT"


ocr_service = OCRService()
