# 🎵 YouTube MP3 Clip

Save approximately **3 minutes of YouTube audio as an MP3** using one command in Google Colab.

No API key required.

> Use only for content you own or have permission to download.

## 🚀 Quick start

Open a Google Colab notebook, paste the following line into a code cell, replace `VIDEO_URL` with your YouTube video link, and run it:

```python
!bash -c 'dir=$(mktemp -d) && git clone -q --depth 1 https://github.com/digimarketingai/youtube-mp3.git "$dir" && bash "$dir/run.sh" "$@"' -- "VIDEO_URL" --start 0 --duration 180
```

The command installs the dependencies and saves the first **180 seconds** of audio to:

```text
/content/audio_clip.mp3
```

Keep the quotation marks around your video URL.

## ⏱️ Choose a different section

To extract 3 minutes starting at **1:00**:

```python
!bash -c 'dir=$(mktemp -d) && git clone -q --depth 1 https://github.com/digimarketingai/youtube-mp3.git "$dir" && bash "$dir/run.sh" "$@"' -- "VIDEO_URL" --start 60 --duration 180
```

### Available options

| Option | Default | Description |
|--------|---------|-------------|
| `--start` | `0` | Start time in seconds |
| `--duration` | `180` | Clip length in seconds |
| `--output` | `/content/audio_clip.mp3` | Output MP3 path |

Example with a custom filename:

```python
!bash -c 'dir=$(mktemp -d) && git clone -q --depth 1 https://github.com/digimarketingai/youtube-mp3.git "$dir" && bash "$dir/run.sh" "$@"' -- "VIDEO_URL" --start 30 --duration 120 --output "/content/my_clip.mp3"
```

This requests a 2-minute clip starting at 0:30.

## 📥 Download the MP3 to your computer

The extraction command saves the MP3 in your Colab session. To download it to your computer, run this in another cell:

```python
from google.colab import files
files.download("/content/audio_clip.mp3")
```

If you used a custom output filename, update the path above.

## 🎧 Listen in Colab

```python
from IPython.display import Audio, display
display(Audio(filename="/content/audio_clip.mp3"))
```

## 📁 Repository files

```text
youtube-mp3/
├── clip.py       # Command-line audio extraction
├── run.sh        # Dependency installation and launcher
└── README.md
```

## 🛠️ Troubleshooting

### Video unavailable or sign-in required

Check that the URL is correct and the video is accessible. YouTube may restrict access from Colab even when a video plays in your browser.

This tool does not bypass sign-in, regional restrictions, or other access controls.

### No audio produced

Make sure your start time is before the end of the video. Start time must be zero or greater, and duration must be greater than zero.

### Download failed

Read the error message in the cell output. Installation, network access, or YouTube extraction may fail.

### An old MP3 is still present

A successful run replaces the selected output file. A failed run may leave a file from an earlier run, so check for the `Saved:` message before downloading.

## 📝 Notes

- Designed for standard hosted Google Colab runtimes.
- Installs yt-dlp, FFmpeg, and Deno.
- Outputs MP3 with a requested audio bitrate of 192 kbps.
- Clip timing is approximate; available audio may be shorter than the requested duration.
- Downloads one video, not an entire playlist.
- Download your MP3 before your Colab session ends; runtime files are temporary.
- Compatibility depends on YouTube and yt-dlp and is not guaranteed for every video.
