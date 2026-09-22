# 🎵 YouTube MP3 Clip — Gradio UI

Create an MP3 audio clip from a YouTube video using a simple web interface.

## Features

- Paste a YouTube video URL.
- Choose the start time.
- Choose a clip length from 1 to 600 seconds.
- Default clip length: 3 minutes.
- Listen to the result in the interface.
- Download the MP3 with one click.
- No API key required.

Only use this tool for content you own or have permission to download.

## 🚀 Run in Google Colab

Paste this single line into a Colab code cell and run it:

```python
!bash -c 'set -e; d=$(mktemp -d); git clone -q --depth 1 https://github.com/digimarketingai/youtube-mp3.git "$d"; bash "$d/run.sh" --share'
```

### How to use it

1. Wait for installation to finish.
2. Open the public Gradio URL printed in the cell output.
3. Paste your YouTube video URL.
4. Choose a start time and duration.
5. Confirm that you have permission to download the content.
6. Click **Create MP3**.
7. Listen to the result or click **Download MP3**.

Keep the Colab cell running while using the interface.
Stop the cell when you are finished.

**Privacy:** The Gradio share link is public, not password-protected.
Anyone with the link can use the running interface. Do not distribute it
unless you intend to share access to your Colab resources.

## ⏱️ Clip examples

| Start time | Duration | Requested section |
|------------|----------|-------------------|
| 0 | 180 | 0:00–3:00 |
| 60 | 180 | 1:00–4:00 |
| 30 | 120 | 0:30–2:30 |

All values are in seconds.

Clip boundaries are approximate. If a video ends before the requested
end time, the result may be shorter.

## 📁 Repository structure

```text
youtube-mp3/
├── app.py
├── run.sh
├── requirements.txt
├── .gitignore
└── README.md
```

## How it works

- `run.sh` installs dependencies and starts the app.
- `app.py` provides the Gradio interface.
- yt-dlp retrieves the requested audio section.
- FFmpeg converts the result to MP3.
- Each request uses its own output directory.

The app requests MP3 encoding at 192 kbps. Re-encoding does not improve
the quality of the original audio.

## 🛠️ Troubleshooting

### “Sign in to confirm you’re not a bot” or “Video unavailable”

YouTube may restrict access from Colab. A video playing in your browser
does not guarantee it can be downloaded from the Colab runtime.

This app does not bypass sign-in, regional restrictions, or access controls.

### No audio was produced

Check that the start time is before the end of the video.

### Request timed out

Jobs are stopped after 10 minutes. Try a shorter clip or another
accessible video.

### No Gradio link appears

Check the cell output for installation or network errors.
Stop the cell before restarting it.

### Storage usage

Successful MP3 files remain in the app's `outputs/` folder for the
runtime session. Restart the runtime to clear accumulated files.

## Limitations

- Designed for standard hosted Google Colab/Linux environments.
- Requires internet access.
- Live streams are rejected.
- Processes one conversion at a time.
- Maximum requested clip length: 10 minutes.
- YouTube extraction is not guaranteed for every video.
- The public interface is intended for temporary personal use, not
  unattended public hosting.
