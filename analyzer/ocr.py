"""OCR 모듈 — 한국어 ONNX 모델 번들 (tesseract 불필요).

RapidOCR + 한국어 PaddleOCR ONNX 모델로 동작.
외부 설치 없이 바이너리에 모두 포함.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# 모델 경로 — PyInstaller 번들/개발 모드 모두 지원
if getattr(sys, "frozen", False):
    _BASE = Path(sys._MEIPASS)
else:
    _BASE = Path(__file__).resolve().parent.parent

_KOREAN_REC_MODEL = _BASE / "models" / "korean" / "rec_model.onnx"
_KOREAN_DICT = _BASE / "models" / "korean" / "dict.txt"

_ocr_instance = None


def _get_ocr():
    """한국어 모델로 RapidOCR 인스턴스 생성 (싱글톤)."""
    global _ocr_instance
    if _ocr_instance is not None:
        return _ocr_instance

    from rapidocr_onnxruntime import RapidOCR
    from rapidocr_onnxruntime.utils import read_yaml, concat_model_path
    import rapidocr_onnxruntime

    pkg_dir = Path(rapidocr_onnxruntime.__file__).resolve().parent
    config = read_yaml(str(pkg_dir / "config.yaml"))
    config = concat_model_path(config)

    # 한국어 인식 모델로 교체
    if _KOREAN_REC_MODEL.exists() and _KOREAN_DICT.exists():
        config["Rec"]["model_path"] = str(_KOREAN_REC_MODEL)
        config["Rec"]["keys_path"] = str(_KOREAN_DICT)
        logger.info("한국어 OCR 모델 로드: %s", _KOREAN_REC_MODEL.name)
    else:
        logger.warning("한국어 모델 없음 — 기본 모델 사용")

    # config를 직접 주입하여 생성 (kwargs 파싱 우회)
    ocr = object.__new__(RapidOCR)
    ocr._init_from_config(config)
    _ocr_instance = ocr
    return _ocr_instance


def _init_rapidocr_from_config(config: dict):
    """RapidOCR를 config dict로 직접 초기화."""
    from rapidocr_onnxruntime import RapidOCR
    from rapidocr_onnxruntime.utils import LoadImage

    ocr = object.__new__(RapidOCR)

    global_config = config["Global"]
    ocr.print_verbose = global_config["print_verbose"]
    ocr.text_score = global_config["text_score"]
    ocr.min_height = global_config["min_height"]
    ocr.width_height_ratio = global_config["width_height_ratio"]

    ocr.use_text_det = global_config["use_text_det"]
    if ocr.use_text_det:
        TextDetector = ocr.init_module(config["Det"]["module_name"], config["Det"]["class_name"])
        ocr.text_detector = TextDetector(config["Det"])

    TextRecognizer = ocr.init_module(config["Rec"]["module_name"], config["Rec"]["class_name"])
    ocr.text_recognizer = TextRecognizer(config["Rec"])

    ocr.use_angle_cls = global_config["use_angle_cls"]
    if ocr.use_angle_cls:
        TextClassifier = ocr.init_module(config["Cls"]["module_name"], config["Cls"]["class_name"])
        ocr.text_cls = TextClassifier(config["Cls"])

    ocr.load_img = LoadImage()
    return ocr


def ocr_image(image_bytes: bytes) -> str:
    """이미지에서 텍스트 추출 (한국어 ONNX 모델)."""
    try:
        ocr = _get_ocr_safe()
        result, _ = ocr(image_bytes)

        if not result:
            return "(이미지에서 텍스트를 인식하지 못했습니다)"

        lines = [item[1] for item in result]
        text = "\n".join(lines)
        logger.info("OCR 완료: %d줄, %d자", len(lines), len(text))
        return text

    except ImportError:
        return "(OCR 라이브러리가 없습니다. rapidocr-onnxruntime을 설치하세요.)"
    except Exception as e:
        logger.exception("OCR 실패: %s", e)
        return f"(OCR 처리 중 오류: {e})"


def _get_ocr_safe():
    """한국어 모델로 RapidOCR 인스턴스 생성 (싱글톤)."""
    global _ocr_instance
    if _ocr_instance is not None:
        return _ocr_instance

    from rapidocr_onnxruntime.utils import read_yaml, concat_model_path
    import rapidocr_onnxruntime

    pkg_dir = Path(rapidocr_onnxruntime.__file__).resolve().parent
    config = read_yaml(str(pkg_dir / "config.yaml"))
    config = concat_model_path(config)

    # 한국어 인식 모델로 교체
    if _KOREAN_REC_MODEL.exists() and _KOREAN_DICT.exists():
        config["Rec"]["model_path"] = str(_KOREAN_REC_MODEL)
        config["Rec"]["keys_path"] = str(_KOREAN_DICT)
        logger.info("한국어 OCR 모델 로드: %s", _KOREAN_REC_MODEL.name)
    else:
        logger.warning("한국어 모델 없음 — 기본 모델 사용")

    _ocr_instance = _init_rapidocr_from_config(config)
    return _ocr_instance
