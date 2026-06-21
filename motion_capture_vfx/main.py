"""CLI entry point for the motion capture + VFX pipeline."""

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m motion_capture_vfx",
        description=(
            "Motion capture + VFX synthesis: animate a reference photo with the motion "
            "from a source video, producing a new video where the photo subject performs "
            "the same movements."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m motion_capture_vfx --video dance.mp4 --photo actor.jpg --output result.mp4
  python -m motion_capture_vfx --video walk.mp4  --photo model.jpg  --output out.mp4 --blend 0.85
  python -m motion_capture_vfx --video walk.mp4  --photo model.jpg  --output out.mp4 --skip-face-swap

Notes:
  - The reference photo should show a full-body, front-facing person for best results.
  - CPU processing takes ~1-3 seconds per frame at 720p resolution.
  - InsightFace models (~500 MB) are downloaded on first use to ~/.insightface/models/.
  - ffmpeg must be installed on your system for audio preservation.
        """,
    )
    p.add_argument("--video", required=True, metavar="PATH", help="Source video (person A — provides motion)")
    p.add_argument("--photo", required=True, metavar="PATH", help="Reference photo (person B — provides appearance)")
    p.add_argument("--output", required=True, metavar="PATH", help="Output video path (e.g. result.mp4)")
    p.add_argument(
        "--blend", type=float, default=0.9, metavar="FLOAT",
        help="Body blend strength 0.0–1.0 (default: 0.9). Lower values preserve more of the original background.",
    )
    p.add_argument(
        "--skip-face-swap", action="store_true",
        help="Disable InsightFace face swap; use body-warp only (faster, no model download required).",
    )
    p.add_argument(
        "--no-audio", action="store_true",
        help="Do not copy audio from the source video to the output.",
    )
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Basic validation before loading heavy models.
    errors = []
    if not Path(args.video).is_file():
        errors.append(f"Video not found: {args.video}")
    if not Path(args.photo).is_file():
        errors.append(f"Photo not found: {args.photo}")
    if not (0.0 <= args.blend <= 1.0):
        errors.append(f"--blend must be between 0.0 and 1.0, got {args.blend}")
    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    from .pipeline import MotionCapturePipeline

    pipeline = MotionCapturePipeline(
        video_path=args.video,
        photo_path=args.photo,
        output_path=args.output,
        blend_strength=args.blend,
        skip_face_swap=args.skip_face_swap,
        no_audio=args.no_audio,
    )
    pipeline.run()


if __name__ == "__main__":
    main()
