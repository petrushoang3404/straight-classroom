"""Face detection, run against the real model.

Skipped when the weights haven't been fetched (`make be-fetch-weights`), so a
checkout without them still has a green suite.
"""

from pathlib import Path

import cv2
import numpy as np
import pytest

from backend.config import settings
from backend.inference import InvalidImageError, detect_faces

pytestmark = pytest.mark.skipif(
    not settings.face_model_path.is_file(), reason="face model weights not fetched"
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_finds_every_face_with_boxes_inside_the_image():
    detection = detect_faces((FIXTURES / "two_faces.jpg").read_bytes())

    assert detection.count == 2
    for face in detection.faces:
        assert 0 <= face.x1 < face.x2 <= detection.width
        assert 0 <= face.y1 < face.y2 <= detection.height
        assert 0.4 <= face.confidence <= 1


def test_no_faces_in_a_blank_image():
    _, blank = cv2.imencode(".png", np.full((480, 640, 3), 200, dtype=np.uint8))

    detection = detect_faces(blank.tobytes())

    assert detection.count == 0
    assert (detection.width, detection.height) == (640, 480)


def test_rejects_bytes_that_are_not_an_image():
    with pytest.raises(InvalidImageError):
        detect_faces(b"definitely not an image")
