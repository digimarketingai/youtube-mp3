import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Save a YouTube audio clip as MP3."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--start", type=int, default=0,
                        help="Start time in seconds (default: 0)")
    parser.add_argument("--duration", type=int, default=180,
                        help="Clip length in seconds (default: 180)")
    parser.add_argument("--output", default="/content/audio_clip.mp3",
                        help="Output MP3 path")
    args = parser.parse_args()

    if args.start < 0 or args.duration <= 0:
        parser.error("--start must be >= 0 and --duration must be > 0")

    output = Path(args.output).expanduser().resolve()
    if output.suffix.lower() != ".mp3":
        parser.error("--output must end with .mp3")

    output.parent.mkdir(parents=True, exist_ok=True)

    # A temporary folder prevents reuse of an older download.
    with tempfile.TemporaryDirectory(prefix="youtube_mp3_") as folder:
        template = str(Path(folder) / "clip.%(ext)s")

        command = [
            sys.executable, "-m", "yt_dlp",
            "--ignore-config",
            "--no-playlist",
            "--js-runtimes", "deno",
            "--socket-timeout", "30",
            "--retries", "2",
            "-f", "bestaudio/best",
            "--download-sections",
            f"*{args.start}-{args.start + args.duration}",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "-o", template,
            "--", args.url,
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            print(
                "\nDownload failed. See the error above. "
                "No new MP3 was saved.",
                file=sys.stderr,
            )
            return 1

        result = Path(folder) / "clip.mp3"
        if not result.is_file() or result.stat().st_size == 0:
            print("No audio produced. Check the time range.", file=sys.stderr)
            return 1

        shutil.copyfile(result, output)

    print(f"\nSaved: {output}")
    print(f"Size: {output.stat().st_size / 1024 / 1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
