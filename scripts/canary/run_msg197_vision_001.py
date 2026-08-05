from __future__ import annotations

import hashlib
import importlib.metadata
import json
import resource
import socket
import sys
import time
from typing import Any

import numpy as np


def _deny_network(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError("network access denied by MSG197-VISION-001 canary")


socket.create_connection = _deny_network  # type: ignore[assignment]
socket.socket.connect = _deny_network  # type: ignore[assignment]

started = time.perf_counter()
import supervision as sv
from supervision._cv2 import BACKEND_NAME

import_ms = (time.perf_counter() - started) * 1000.0

installed = sorted(
    {
        distribution.metadata["Name"].lower()
        for distribution in importlib.metadata.distributions()
        if distribution.metadata.get("Name")
    }
)
for forbidden in (
    "torch",
    "tensorflow",
    "ultralytics",
    "transformers",
    "inference",
    "roboflow",
):
    if forbidden in installed:
        raise RuntimeError(f"forbidden model or remote-inference package installed: {forbidden}")

if BACKEND_NAME != "fallback":
    raise RuntimeError(f"expected pure NumPy fallback backend, observed {BACKEND_NAME}")

xyxy = np.array(
    [
        [2.0, 3.0, 20.0, 24.0],
        [4.0, 5.0, 18.0, 22.0],
        [30.0, 31.0, 50.0, 54.0],
    ],
    dtype=np.float32,
)
confidence = np.array([0.95, 0.80, 0.70], dtype=np.float32)
class_id = np.array([1, 1, 2], dtype=np.int32)
detections = sv.Detections(xyxy=xyxy, confidence=confidence, class_id=class_id)

op_started = time.perf_counter()
iou = sv.box_iou_batch(xyxy, xyxy)
nms_predictions = np.column_stack((xyxy, confidence, class_id)).astype(np.float32)
nms = sv.box_non_max_suppression(
    predictions=nms_predictions,
    iou_threshold=0.5,
)
xywh = sv.xyxy_to_xywh(xyxy)
scene = np.zeros((64, 64, 3), dtype=np.uint8)
annotated = sv.BoxAnnotator(thickness=2).annotate(
    scene=scene.copy(),
    detections=detections,
)
operation_ms = (time.perf_counter() - op_started) * 1000.0

payload = {
    "schema_version": "1.0.0",
    "mission_id": "MSG197-VISION-001",
    "python": sys.version.split()[0],
    "supervision_version": sv.__version__,
    "backend": BACKEND_NAME,
    "network_policy": "DENIED_BY_CONTAINER_AND_PYTHON_GUARD",
    "model_packages_present": [],
    "synthetic_detection_count": len(detections),
    "iou_sha256": hashlib.sha256(iou.tobytes()).hexdigest(),
    "nms_sha256": hashlib.sha256(np.asarray(nms).tobytes()).hexdigest(),
    "xywh_sha256": hashlib.sha256(xywh.tobytes()).hexdigest(),
    "annotated_image_sha256": hashlib.sha256(annotated.tobytes()).hexdigest(),
    "annotated_shape": list(annotated.shape),
    "import_ms": round(import_ms, 3),
    "synthetic_operation_ms": round(operation_ms, 3),
    "peak_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
    "installed_distribution_count": len(installed),
    "truth_state": "PASS_SYNTHETIC_NO_MODEL_CANARY",
}
print(json.dumps(payload, sort_keys=True))
