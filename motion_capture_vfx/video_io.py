"""Video reading, writing, and audio handling utilities."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator, Tuple

import cv2
import numpy as np


class VideoReader:
    def __init__(self, path: str):
        self.path = path
        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")

    @property
    def fps(self) -> float:
        return self._cap.get(cv2.CAP_PROP_FPS)

    @property
    def width(self) -> int:
        return int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self) -> int:
        return int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def frame_count(self) -> int:
        return int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def frames(self) -> Generator[Tuple[int, np.ndarray], None, None]:
        idx = 0
        while True:
            ok, frame = self._cap.read()
            if not ok:
                break
            yield idx, frame
            idx += 1

    def close(self):
        self._cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class VideoWriter:
    def __init__(self, path: str, fps: float, width: int, height: int):
        self.path = path
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self._writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
        if not self._writer.isOpened():
            raise RuntimeError(f"Cannot open VideoWriter for: {path}")

    def write_frame(self, frame: np.ndarray):
        self._writer.write(frame)

    def close(self):
        self._writer.release()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def extract_audio(video_path: str, out_path: str) -> bool:
    """Extract audio track from video. Returns True if audio was found."""
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "copy", out_path],
        capture_output=True,
    )
    return result.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0


def mux_audio(video_path: str, audio_path: str, out_path: str):
    """Combine a silent video with an audio track into the final output."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            out_path,
        ],
        capture_output=True,
        check=True,
    )


def get_temp_path(suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path
