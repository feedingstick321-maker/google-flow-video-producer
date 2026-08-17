#!/usr/bin/env python3
"""Normalize storyboard clips and concatenate them while preserving audio."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(command: list[str]) -> None:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "ffmpeg command failed")


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate",
            "-of",
            "json",
            str(path),
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"ffprobe failed for {path}")
    return json.loads(result.stdout)


def normalize_clip(
    source: Path,
    destination: Path,
    target_duration: float,
    width: int,
    height: int,
    fps: int,
    allow_slowdown: bool,
) -> None:
    metadata = probe(source)
    source_duration = float(metadata["format"]["duration"])
    has_audio = any(stream.get("codec_type") == "audio" for stream in metadata.get("streams", []))
    slow = allow_slowdown and source_duration + 0.05 < target_duration
    scale = target_duration / source_duration if slow else 1.0

    video_filters = [
        f"scale={width}:{height}:force_original_aspect_ratio=decrease",
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
        f"fps={fps}",
    ]
    if slow:
        video_filters.append(f"setpts={scale:.8f}*PTS")

    command = ["ffmpeg", "-y", "-i", str(source)]
    if not has_audio:
        command += [
            "-f",
            "lavfi",
            "-t",
            f"{target_duration:.6f}",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
        ]

    command += ["-map", "0:v:0", "-vf", ",".join(video_filters)]
    if has_audio:
        audio_filters = []
        if slow:
            tempo = source_duration / target_duration
            audio_filters.append(f"atempo={tempo:.8f}")
        audio_filters += [
            f"apad=pad_dur={target_duration:.6f}",
            f"atrim=0:{target_duration:.6f}",
            "aresample=48000",
            "aformat=channel_layouts=stereo",
        ]
        command += ["-map", "0:a:0", "-af", ",".join(audio_filters)]
    else:
        command += ["-map", "1:a:0"]

    command += [
        "-t",
        f"{target_duration:.6f}",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        str(destination),
    ]
    run(command)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe must be available on PATH")

    manifest_path = args.manifest.resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    width = int(data.get("width", 1280))
    height = int(data.get("height", 720))
    fps = int(data.get("fps", 24))
    clips = data.get("clips", [])
    if not clips:
        raise SystemExit("manifest has no clips")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="flow-assemble-", dir=output.parent) as temp_name:
        temp = Path(temp_name)
        normalized: list[Path] = []
        for index, clip in enumerate(clips, start=1):
            source = (manifest_path.parent / clip["path"]).resolve()
            if not source.is_file():
                raise FileNotFoundError(source)
            destination = temp / f"{index:03d}-{clip.get('id', 'shot')}.mp4"
            normalize_clip(
                source,
                destination,
                float(clip["target_duration"]),
                width,
                height,
                fps,
                bool(clip.get("allow_slowdown", False)),
            )
            normalized.append(destination)

        concat_file = temp / "concat.txt"
        concat_file.write_text(
            "".join(f"file '{path.as_posix()}'\n" for path in normalized),
            encoding="utf-8",
        )
        run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )

    summary = probe(output)
    print(json.dumps({"status": "ok", "output": str(output), "media": summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

