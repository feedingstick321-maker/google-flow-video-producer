#!/usr/bin/env python3
"""Return deterministic ffprobe metadata for one or more video files."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def inspect(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate",
            "-of",
            "json",
            str(path),
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        return {"path": str(path), "status": "error", "message": result.stderr.strip()}
    data = json.loads(result.stdout)
    return {
        "path": str(path.resolve()),
        "status": "ok",
        "duration": float(data.get("format", {}).get("duration", 0)),
        "size": int(data.get("format", {}).get("size", 0)),
        "streams": data.get("streams", []),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("videos", nargs="+", type=Path)
    args = parser.parse_args()
    if not shutil.which("ffprobe"):
        raise SystemExit("ffprobe must be available on PATH")
    print(json.dumps([inspect(path) for path in args.videos], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

