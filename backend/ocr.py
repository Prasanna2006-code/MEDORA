from pathlib import Path
from typing import Dict, Any

import pytesseract
from PIL import Image


def extract_text_from_image(image_path: str) -> Dict[str, Any]:
    path = Path(image_path)

    if not path.exists():
        return {
            "success": False,
            "text": "",
            "message": "Image file not found"
        }

    try:
        image = Image.open(path)
        text = pytesseract.image_to_string(image).strip()

        return {
            "success": True,
            "text": text,
            "message": "Text extracted successfully"
        }

    except Exception as error:
        return {
            "success": False,
            "text": "",
            "message": str(error)
        }


def extract_patient_information(image_path: str) -> Dict[str, Any]:
    result = extract_text_from_image(image_path)

    if not result["success"]:
        return result

    text = result["text"]

    return {
        "success": True,
        "text": text,
        "patient_information": {
            "name": None,
            "age": None,
            "sex": None,
            "symptoms": None,
            "disorders": None
        }
    }


def ocr_health() -> Dict[str, Any]:
    return {
        "service": "MEDORA OCR Service",
        "status": "ready"
    }