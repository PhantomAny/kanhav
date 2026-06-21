"""InsightFace-based face detection and swapping."""

import os
from typing import Optional

import cv2
import numpy as np

try:
    import insightface
    from insightface.app import FaceAnalysis
    _INSIGHTFACE_AVAILABLE = True
except ImportError:
    _INSIGHTFACE_AVAILABLE = False


class FaceSwapper:
    def __init__(self, model_pack: str = "buffalo_l"):
        if not _INSIGHTFACE_AVAILABLE:
            raise RuntimeError(
                "insightface is not installed. Run: pip install insightface onnxruntime"
            )
        self._app = FaceAnalysis(name=model_pack, providers=["CPUExecutionProvider"])
        self._app.prepare(ctx_id=0, det_size=(640, 640))

        model_dir = os.path.join(os.path.expanduser("~"), ".insightface", "models")
        swap_model_path = os.path.join(model_dir, "inswapper_128.onnx")
        if not os.path.exists(swap_model_path):
            raise RuntimeError(
                f"Face swap model not found at {swap_model_path}.\n"
                "Download inswapper_128.onnx from the InsightFace model zoo and place it there."
            )
        self._swapper = insightface.model_zoo.get_model(swap_model_path, providers=["CPUExecutionProvider"])

    def extract_source_face(self, photo_bgr: np.ndarray):
        """Detect and return the primary face object from the reference photo."""
        faces = self._app.get(photo_bgr)
        if not faces:
            return None
        # Return the largest detected face.
        return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))

    def swap_face(self, frame_bgr: np.ndarray, source_face) -> np.ndarray:
        """
        Swap all faces in frame_bgr with source_face.
        Returns the modified frame, or the original if no face is detected.
        """
        if source_face is None:
            return frame_bgr

        faces = self._app.get(frame_bgr)
        if not faces:
            return frame_bgr

        result = frame_bgr.copy()
        for face in faces:
            result = self._swapper.get(result, face, source_face, paste_back=True)
        return result
