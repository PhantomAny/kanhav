"""MediaPipe Holistic wrapper for pose landmark extraction."""

from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

# Indices into the 33-landmark MediaPipe pose model.
# We use a stable subset as TPS control points (skip unstable face/hand tips).
CONTROL_POINT_INDICES = [
    0,   # nose
    11,  # left shoulder
    12,  # right shoulder
    13,  # left elbow
    14,  # right elbow
    15,  # left wrist
    16,  # right wrist
    23,  # left hip
    24,  # right hip
    25,  # left knee
    26,  # right knee
    27,  # left ankle
    28,  # right ankle
]


class PoseExtractor:
    def __init__(self):
        self._holistic = mp.solutions.holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._holistic_static = mp.solutions.holistic.Holistic(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5,
        )

    def extract_frame_landmarks(self, bgr_frame: np.ndarray) -> Optional[np.ndarray]:
        """Return (33, 2) pixel coords for a video frame, or None if not detected."""
        return self._run(bgr_frame, static=False)

    def extract_photo_landmarks(self, bgr_image: np.ndarray) -> Optional[np.ndarray]:
        """Return (33, 2) pixel coords for a static photo, or None if not detected."""
        return self._run(bgr_image, static=True)

    def _run(self, bgr: np.ndarray, static: bool) -> Optional[np.ndarray]:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w = bgr.shape[:2]
        model = self._holistic_static if static else self._holistic
        result = model.process(rgb)
        if result.pose_landmarks is None:
            return None
        coords = np.array(
            [[lm.x * w, lm.y * h] for lm in result.pose_landmarks.landmark],
            dtype=np.float32,
        )
        return coords

    def get_control_points(self, landmarks: np.ndarray) -> np.ndarray:
        """Return the stable subset of landmarks used as TPS control points."""
        return landmarks[CONTROL_POINT_INDICES]

    def close(self):
        self._holistic.close()
        self._holistic_static.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
