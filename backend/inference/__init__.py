"""In-process inference. Callers import and call these directly; there is no
HTTP service in between."""

from backend.inference.detector import (
    Detection,
    Face,
    InvalidImageError,
    detect_faces,
    load_model,
)

__all__ = ["Detection", "Face", "InvalidImageError", "detect_faces", "load_model"]
