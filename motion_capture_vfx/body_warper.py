"""Pose-driven body warping using Thin Plate Spline interpolation."""

from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np
from scipy.interpolate import RBFInterpolator


class BodyWarper:
    def __init__(self, photo_bgr: np.ndarray, photo_control_points: np.ndarray):
        """
        photo_bgr: the reference appearance image (person B)
        photo_control_points: (N, 2) landmark pixel coords in the photo
        """
        self._photo = photo_bgr
        self._photo_pts = photo_control_points
        self._photo_h, self._photo_w = photo_bgr.shape[:2]

    def warp_to_frame(
        self,
        target_control_points: np.ndarray,
        target_shape: Tuple[int, int],
    ) -> np.ndarray:
        """
        Warp the reference photo to match the pose in the target frame.
        target_control_points: (N, 2) pixel coords in the target frame
        target_shape: (height, width) of the output
        Returns a BGR image of size target_shape.
        """
        th, tw = target_shape

        # Normalise both point sets to [0,1] so the RBF is scale-invariant.
        src_norm = self._photo_pts / np.array([self._photo_w, self._photo_h], dtype=np.float32)
        dst_norm = target_control_points / np.array([tw, th], dtype=np.float32)

        valid = self._valid_pairs(src_norm, dst_norm)
        if valid.sum() < 4:
            return self._affine_fallback(target_control_points, target_shape)

        src_v = src_norm[valid]
        dst_v = dst_norm[valid]

        if valid.sum() >= 8:
            # TPS via RBF: fit mapping  dst → src  (inverse warp)
            rbf_x = RBFInterpolator(dst_v, src_v[:, 0], kernel="thin_plate_spline", smoothing=1e-4)
            rbf_y = RBFInterpolator(dst_v, src_v[:, 1], kernel="thin_plate_spline", smoothing=1e-4)

            gy, gx = np.mgrid[0:th, 0:tw]
            grid_pts = np.stack([gx / tw, gy / th], axis=-1).reshape(-1, 2)

            map_x = (rbf_x(grid_pts) * self._photo_w).reshape(th, tw).astype(np.float32)
            map_y = (rbf_y(grid_pts) * self._photo_h).reshape(th, tw).astype(np.float32)
        else:
            return self._affine_fallback(target_control_points, target_shape)

        warped = cv2.remap(
            self._photo, map_x, map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )
        return warped

    def _valid_pairs(self, src: np.ndarray, dst: np.ndarray) -> np.ndarray:
        """Mask out pairs where either point is far outside [0,1]."""
        src_ok = np.all((src > -0.1) & (src < 1.1), axis=1)
        dst_ok = np.all((dst > -0.1) & (dst < 1.1), axis=1)
        return src_ok & dst_ok

    def _affine_fallback(
        self,
        target_control_points: np.ndarray,
        target_shape: Tuple[int, int],
    ) -> np.ndarray:
        th, tw = target_shape
        # Estimate affine from up to 3 best-confidence point pairs.
        n = min(3, len(self._photo_pts), len(target_control_points))
        src3 = self._photo_pts[:n].astype(np.float32)
        dst3 = target_control_points[:n].astype(np.float32)
        M = cv2.getAffineTransform(src3, dst3)
        return cv2.warpAffine(self._photo, M, (tw, th), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT_101)


class SegmentationMask:
    def __init__(self):
        self._seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

    def get_mask(self, bgr_frame: np.ndarray) -> np.ndarray:
        """Return float32 mask in [0,1] with 1 = person, 0 = background."""
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        result = self._seg.process(rgb)
        mask = result.segmentation_mask  # already float32
        # Smooth edges
        mask = cv2.GaussianBlur(mask, (15, 15), 5)
        return mask

    def close(self):
        self._seg.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
