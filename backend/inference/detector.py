"""Face detection with a YOLOv8 face model on ONNX Runtime.

Detection only: it says where faces are, never whose they are.
"""

from dataclasses import dataclass
from functools import cache

import cv2
import numpy as np
import onnxruntime as ort

from backend.config import settings

INPUT_SIZE = 640
PAD_VALUE = 114  # the grey YOLO models are trained with
NMS_IOU_THRESHOLD = 0.45


class InvalidImageError(ValueError):
    """The bytes are not an image we can decode."""


@dataclass(frozen=True)
class Face:
    """A box in pixels of the original image."""

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float


@dataclass(frozen=True)
class Detection:
    width: int
    height: int
    faces: list[Face]

    @property
    def count(self) -> int:
        return len(self.faces)


@cache
def load_model() -> ort.InferenceSession:
    """Load the model once. Sessions are thread-safe, so callers share it."""
    path = settings.face_model_path
    if not path.is_file():
        raise RuntimeError(
            f"Face model not found at {path}; run `make be-fetch-weights`"
        )
    return ort.InferenceSession(path, providers=["CPUExecutionProvider"])


def detect_faces(image_bytes: bytes) -> Detection:
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImageError("Not a readable image")
    height, width = image.shape[:2]

    blob, scale, pad_x, pad_y = _letterbox(image)
    (output,) = load_model().run(None, {"images": blob})

    # (1, 5, anchors) -> one row per anchor: centre x, centre y, w, h, score.
    rows = output[0].T
    rows = rows[rows[:, 4] >= settings.face_conf_threshold]

    # Undo the letterbox, then clip to the image.
    x1 = np.clip((rows[:, 0] - rows[:, 2] / 2 - pad_x) / scale, 0, width)
    y1 = np.clip((rows[:, 1] - rows[:, 3] / 2 - pad_y) / scale, 0, height)
    x2 = np.clip((rows[:, 0] + rows[:, 2] / 2 - pad_x) / scale, 0, width)
    y2 = np.clip((rows[:, 1] + rows[:, 3] / 2 - pad_y) / scale, 0, height)
    scores = rows[:, 4]

    boxes_xywh = np.stack([x1, y1, x2 - x1, y2 - y1], axis=1)
    keep = cv2.dnn.NMSBoxes(
        boxes_xywh.tolist(),
        scores.tolist(),
        settings.face_conf_threshold,
        NMS_IOU_THRESHOLD,
    )
    faces = [
        Face(float(x1[i]), float(y1[i]), float(x2[i]), float(y2[i]), float(scores[i]))
        for i in np.asarray(keep, dtype=int).flatten()
    ]
    return Detection(width=width, height=height, faces=faces)


def _letterbox(image: np.ndarray) -> tuple[np.ndarray, float, float, float]:
    """Fit the image into a square without distorting it.

    Returns the input blob plus the scale and padding needed to map boxes back.
    """
    height, width = image.shape[:2]
    scale = INPUT_SIZE / max(height, width)
    new_w, new_h = round(width * scale), round(height * scale)
    pad_x, pad_y = (INPUT_SIZE - new_w) / 2, (INPUT_SIZE - new_h) / 2

    canvas = np.full((INPUT_SIZE, INPUT_SIZE, 3), PAD_VALUE, dtype=np.uint8)
    top, left = int(pad_y), int(pad_x)
    canvas[top : top + new_h, left : left + new_w] = cv2.resize(image, (new_w, new_h))

    blob = cv2.dnn.blobFromImage(canvas, 1 / 255, swapRB=True)
    return blob, scale, left, top
