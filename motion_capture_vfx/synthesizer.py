"""Per-frame VFX composition: blending, color correction, and edge smoothing."""

import cv2
import numpy as np


class Synthesizer:
    def __init__(self, blend_strength: float = 0.9):
        self.blend_strength = blend_strength

    def compose(
        self,
        original_frame: np.ndarray,
        warped_photo: np.ndarray,
        segmentation_mask: np.ndarray,
        face_swapped: np.ndarray,
    ) -> np.ndarray:
        """
        Compose the final frame:
        1. Color-correct warped_photo to match original lighting.
        2. Blend warped body into the background using segmentation mask.
        3. Overlay the face-swapped result in the face region.
        """
        h, w = original_frame.shape[:2]

        # Resize warped photo to match frame if necessary.
        if warped_photo.shape[:2] != (h, w):
            warped_photo = cv2.resize(warped_photo, (w, h), interpolation=cv2.INTER_LINEAR)
        if face_swapped is not None and face_swapped.shape[:2] != (h, w):
            face_swapped = cv2.resize(face_swapped, (w, h), interpolation=cv2.INTER_LINEAR)

        # Color correct the warped photo to match original frame illumination.
        corrected = self._color_correct(warped_photo, original_frame, segmentation_mask)

        # Build alpha mask: person region scaled by blend_strength.
        alpha = np.clip(segmentation_mask * self.blend_strength, 0, 1)
        alpha3 = alpha[:, :, np.newaxis]

        # Composite body.
        result = (corrected.astype(np.float32) * alpha3
                  + original_frame.astype(np.float32) * (1.0 - alpha3)).astype(np.uint8)

        # Overlay face-swap result where the face was swapped.
        if face_swapped is not None:
            # The face swapper already handled blending internally; use it directly
            # in the person mask region only.
            result = (face_swapped.astype(np.float32) * alpha3
                      + original_frame.astype(np.float32) * (1.0 - alpha3)).astype(np.uint8)

        return result

    def _color_correct(
        self,
        source: np.ndarray,
        target: np.ndarray,
        mask: np.ndarray,
    ) -> np.ndarray:
        """
        Match the histogram of source (in masked region) to target,
        to compensate for lighting differences between the photo and video.
        """
        mask_bin = (mask > 0.5).astype(np.uint8)
        if mask_bin.sum() < 100:
            return source

        result = source.copy().astype(np.float32)
        for c in range(3):
            src_vals = source[:, :, c][mask_bin == 1].astype(np.float32)
            tgt_vals = target[:, :, c][mask_bin == 1].astype(np.float32)
            if src_vals.std() < 1e-3:
                continue
            # Simple mean/std matching (Reinhard-style per channel).
            src_mean, src_std = src_vals.mean(), src_vals.std()
            tgt_mean, tgt_std = tgt_vals.mean(), tgt_vals.std()
            scale = tgt_std / (src_std + 1e-6)
            result[:, :, c] = (result[:, :, c] - src_mean) * scale + tgt_mean

        return np.clip(result, 0, 255).astype(np.uint8)
