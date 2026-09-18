from pathlib import Path
from typing import Dict, Any

import speech_recognition as sr


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    path = Path(audio_path)

    if not path.exists():
        return {
            "success": False,
            "text": "",
            "message": "Audio file not found"
        }

    try:
        recognizer = sr.Recognizer()

        with sr.AudioFile(str(path)) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)

        return {
            "success": True,
            "text": text,
            "message": "Speech converted to text successfully"
        }

    except sr.UnknownValueError:
        return {
            "success": False,
            "text": "",
            "message": "Speech could not be understood"
        }

    except sr.RequestError:
        return {
            "success": False,
            "text": "",
            "message": "Speech recognition service unavailable"
        }

    except Exception as error:
        return {
            "success": False,
            "text": "",
            "message": str(error)
        }


def voice_health() -> Dict[str, Any]:
    return {
        "service": "MEDORA Voice Service",
        "status": "ready"
    }