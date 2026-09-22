import argparse
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import gradio as gr


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_DURATION = 600       # Maximum 10 minutes per request
JOB_TIMEOUT = 600        # Stop a job after 10 minutes


def normalize_youtube_url(value):
    """Accept video links only and rebuild a clean YouTube URL."""
    value = (value or "").strip()

    if not value:
        raise ValueError("Paste a YouTube video URL.")

    if "://" not in value:
        value = "https://" + value

    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    parts = parsed.path.strip("/").split("/")
    video_id = None

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Please use an HTTP or HTTPS YouTube URL.")

    if host in {"youtu.be", "www.youtu.be"}:
        video_id = parts[0]

    elif host in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
    }:
        if parsed.path.rstrip("/") == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            video_id = parts[1]

    if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError(
            "Enter a valid YouTube video link, not a channel or playlist."
        )

    return f"https://www.youtube.com/watch?v={video_id}"


def extract_audio(url, start, duration, permission):
    # Clear previous results immediately, including on a failed new request.
    yield None, None, "Checking your request..."

    job_dir = None
    success = False

    try:
        if not permission:
            raise ValueError(
                "Confirm that you own the content or have permission to download it."
            )

        url = normalize_youtube_url(url)

        try:
            start = float(start)
            duration = float(duration)
        except (TypeError, ValueError):
            raise ValueError("Start time and duration must be numbers.")

        if not math.isfinite(start) or start < 0:
            raise ValueError("Start time must be zero or greater.")

        if not math.isfinite(duration) or not 1 <= duration <= MAX_DURATION:
            raise ValueError(
                f"Duration must be between 1 and {MAX_DURATION} seconds."
            )

        if not shutil.which("ffmpeg"):
            raise ValueError("FFmpeg is missing. Restart using run.sh.")

        if not shutil.which("deno"):
            raise ValueError("Deno is missing. Restart using run.sh.")

        job_dir = Path(
            tempfile.mkdtemp(prefix="clip_", dir=str(OUTPUT_DIR))
        )
        log_file = job_dir / "download.log"
        mp3_file = job_dir / "audio_clip.mp3"

        command = [
            sys.executable, "-m", "yt_dlp",
            "--ignore-config",
            "--no-playlist",
            "--no-progress",
            "--no-colors",
            "--js-runtimes", "deno",
            "--socket-timeout", "30",
            "--retries", "2",
            "--fragment-retries", "2",
            "--match-filter", "!is_live",
            "-f", "bestaudio/best",
            "--download-sections", f"*{start:g}-{start + duration:g}",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "-o", str(job_dir / "audio_clip.%(ext)s"),
            "--", url,
        ]

        yield None, None, "Downloading your clip and converting to MP3..."

        # Linux/Colab process group: timeout also stops FFmpeg children.
        with log_file.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

            try:
                return_code = process.wait(timeout=JOB_TIMEOUT)
            finally:
                if process.poll() is None:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait()

        if return_code != 0:
            details = log_file.read_text(
                encoding="utf-8", errors="replace"
            )[-3500:]

            yield (
                None,
                None,
                "Download failed. YouTube may require sign-in or block "
                "access from Colab. This app does not bypass restrictions."
                f"\n\nTechnical details:\n{details}",
            )
            return

        if not mp3_file.is_file() or mp3_file.stat().st_size == 0:
            raise ValueError(
                "No MP3 was produced. Check that the start time is "
                "before the end of the video."
            )

        size_mb = mp3_file.stat().st_size / (1024 * 1024)
        success = True

        yield (
            str(mp3_file),
            str(mp3_file),
            f"Ready! MP3 created ({size_mb:.2f} MB). "
            "Listen below or click Download MP3.",
        )

    except subprocess.TimeoutExpired:
        yield None, None, (
            "The request timed out after 10 minutes. "
            "Try a shorter clip or another accessible video."
        )

    except ValueError as exc:
        yield None, None, str(exc)

    except Exception as exc:
        print(f"Extraction error: {exc}", file=sys.stderr)
        yield None, None, (
            "An unexpected error occurred. Check the Colab cell output."
        )

    finally:
        if job_dir and not success:
            shutil.rmtree(job_dir, ignore_errors=True)


with gr.Blocks(title="YouTube MP3 Clip") as demo:
    gr.Markdown(
        """
        # 🎵 YouTube MP3 Clip
        Paste a YouTube video link, choose a section, and download an MP3.

        **Default: 3 minutes · Maximum: 10 minutes**

        Only download content you own or have permission to use.
        """
    )

    url_input = gr.Textbox(
        label="YouTube video URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    with gr.Row():
        start_input = gr.Number(
            label="Start time in seconds",
            value=0,
            minimum=0,
            precision=0,
        )

        duration_input = gr.Slider(
            label="Clip duration in seconds",
            minimum=1,
            maximum=MAX_DURATION,
            value=180,
            step=1,
        )

    permission_input = gr.Checkbox(
        label="I own this content or have permission to download it.",
        value=False,
    )

    create_button = gr.Button("Create MP3", variant="primary")

    status_output = gr.Textbox(
        label="Status",
        value="Ready. Paste a video URL to begin.",
        interactive=False,
        lines=3,
    )

    audio_output = gr.Audio(
        label="Listen to your clip",
        type="filepath",
        interactive=False,
    )

    download_output = gr.DownloadButton(
        label="Download MP3",
        value=None,
    )

    gr.Markdown(
        """
        **Tips**
        - Start `60` + duration `180` requests the section from 1:00 to 4:00.
        - Clip timing is approximate; shorter videos may produce shorter clips.
        - Live streams are not supported.
        - Download your file before ending your Colab session.
        """
    )

    create_button.click(
        fn=extract_audio,
        inputs=[
            url_input,
            start_input,
            duration_input,
            permission_input,
        ],
        outputs=[
            audio_output,
            download_output,
            status_output,
        ],
        concurrency_limit=1,
        api_name=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio link, needed for hosted Colab.",
    )
    args = parser.parse_args()

    demo.queue(max_size=10).launch(
        share=args.share,
        server_name="127.0.0.1",
        show_error=False,
    )
