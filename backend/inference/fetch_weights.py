"""Download the face model: `make be-fetch-weights`.

Weights are not committed; this fetches them and checks the hash, so a
swapped or truncated file fails loudly.
"""

import hashlib
import urllib.request

from backend.config import settings

# YOLOv8n-face exported to ONNX (AGPL-3.0, from Ultralytics).
URL = "https://huggingface.co/deepghs/yolo-face/resolve/main/yolov8n-face/model.onnx"
SHA256 = "fd27189bfe5750a017648445700473459a6d02e7c3b0a3bfd8a54af77dd3b046"


def main() -> None:
    path = settings.face_model_path
    path.parent.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(URL) as response:
        data = response.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"Checksum mismatch for {URL}: got {digest}")

    path.write_bytes(data)
    print(f"Saved {path} ({len(data) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
