"""OCR 모듈 — 한국어 우선, 폴백 체인.

우선순위:
1. pytesseract + tesseract (한국어 지원, 가장 정확)
2. rapidocr-onnxruntime (tesseract 없을 때, 숫자/영문 위주)
"""

from __future__ import annotations

import logging
from io import BytesIO

from PIL import Image

logger = logging.getLogger(__name__)


def ocr_image(image_bytes: bytes) -> str:
    """이미지에서 텍스트 추출. tesseract 우선, rapidocr 폴백."""
    # 1차: pytesseract (한국어 지원)
    text = _try_tesseract(image_bytes)
    if text:
        return text

    # 2차: RapidOCR (설치 안 되어도 무시)
    text = _try_rapidocr(image_bytes)
    if text:
        return text

    return "(이미지에서 텍스트를 인식하지 못했습니다. tesseract를 설치하면 한국어 OCR이 가능합니다.)"


def _try_tesseract(image_bytes: bytes) -> str | None:
    """pytesseract로 한국어 OCR."""
    try:
        import pytesseract
    except ImportError:
        return None

    try:
        img = Image.open(BytesIO(image_bytes))
        # 한국어 + 영어 + 숫자
        text = pytesseract.image_to_string(img, lang="kor+eng")
        text = text.strip()
        if text:
            logger.info("tesseract OCR 완료: %d자", len(text))
            return text
    except Exception as e:
        logger.warning("tesseract 실패: %s", e)
    return None


def _try_rapidocr(image_bytes: bytes) -> str | None:
    """RapidOCR 폴백 (한국어 약함, 숫자 OK)."""
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        return None

    try:
        ocr = RapidOCR()
        result, _ = ocr(image_bytes)
        if not result:
            return None
        lines = [item[1] for item in result]
        text = "\n".join(lines)
        logger.info("RapidOCR 완료: %d줄, %d자", len(lines), len(text))
        return text
    except Exception as e:
        logger.warning("RapidOCR 실패: %s", e)
    return None
