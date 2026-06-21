"""Main orchestration pipeline for motion capture + VFX synthesis."""

import os
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from tqdm import tqdm

from .video_io import VideoReader, VideoWriter, extract_audio, mux_audio, get_temp_path
from .pose_extractor import PoseExtractor
from .body_warper import BodyWarper, SegmentationMask
from .face_swapper import FaceSwapper
from .synthesizer import Synthesizer


class MotionCapturePipeline:
    def __init__(
        self,
        video_path: str,
        photo_path: str,
        output_path: str,
        blend_strength: float = 0.9,
        skip_face_swap: bool = False,
        no_audio: bool = False,
    ):
        self.video_path = video_path
        self.photo_path = photo_path
        self.output_path = output_path
        self.blend_strength = blend_strength
        self.skip_face_swap = skip_face_swap
        self.no_audio = no_audio

    def run(self):
        print(f"[1/5] Loading reference photo: {self.photo_path}")
        photo = cv2.imread(self.photo_path)
        if photo is None:
            raise ValueError(f"Cannot read photo: {self.photo_path}")

        print("[2/5] Extracting pose landmarks from reference photo...")
        extractor = PoseExtractor()
        photo_landmarks = extractor.extract_photo_landmarks(photo)
        if photo_landmarks is None:
            raise RuntimeError(
                "No person detected in the reference photo. "
                "Please use a clear full-body photo with good lighting."
            )
        photo_control_pts = extractor.get_control_points(photo_landmarks)

        print("[3/5] Initialising processing modules...")
        warper = BodyWarper(photo, photo_control_pts)
        segmenter = SegmentationMask()
        synthesizer = Synthesizer(blend_strength=self.blend_strength)

        face_swapper: Optional[FaceSwapper] = None
        source_face = None
        if not self.skip_face_swap:
            try:
                face_swapper = FaceSwapper()
                source_face = face_swapper.extract_source_face(photo)
                if source_face is None:
                    print("  Warning: no face detected in photo — face swap disabled.")
            except RuntimeError as e:
                print(f"  Warning: face swap unavailable ({e})\n  Continuing with body warp only.")

        print(f"[4/5] Processing video: {self.video_path}")
        reader = VideoReader(self.video_path)
        raw_out = get_temp_path(".mp4")

        skipped = 0
        with VideoWriter(raw_out, reader.fps, reader.width, reader.height) as writer:
            for idx, frame in tqdm(reader.frames(), total=reader.frame_count, unit="frame"):
                frame_landmarks = extractor.extract_frame_landmarks(frame)

                if frame_landmarks is None:
                    # No person detected — copy original frame.
                    writer.write_frame(frame)
                    skipped += 1
                    continue

                frame_control_pts = extractor.get_control_points(frame_landmarks)
                target_shape = (reader.height, reader.width)

                warped = warper.warp_to_frame(frame_control_pts, target_shape)
                mask = segmenter.get_mask(frame)

                if face_swapper is not None and source_face is not None:
                    face_result = face_swapper.swap_face(warped, source_face)
                else:
                    face_result = None

                output = synthesizer.compose(frame, warped, mask, face_result)
                writer.write_frame(output)

        reader.close()
        extractor.close()
        segmenter.close()

        if skipped:
            print(f"  Note: {skipped} frame(s) had no detected person and were copied unchanged.")

        print("[5/5] Assembling final output...")
        if not self.no_audio:
            audio_tmp = get_temp_path(".aac")
            has_audio = extract_audio(self.video_path, audio_tmp)
            if has_audio:
                mux_audio(raw_out, audio_tmp, self.output_path)
                os.remove(audio_tmp)
            else:
                # No audio stream — just rename/copy the silent video.
                import shutil
                shutil.move(raw_out, self.output_path)
                raw_out = None
        else:
            import shutil
            shutil.move(raw_out, self.output_path)
            raw_out = None

        if raw_out and os.path.exists(raw_out):
            os.remove(raw_out)

        print(f"\nDone. Output saved to: {self.output_path}")
