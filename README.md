# YouTube Downloader GUI (yt-dlp + CustomTkinter)

A simple **desktop GUI** for downloading YouTube videos as **MP4** (merged audio+video) and exporting **audio-only** as **MP3** or **WAV**.

> This is an updated version of the older setup guide. fileciteturn1file0

---

## Features

- **Paste URL → Download** (no command line once running)
- Quality presets: **Best**, **720p (progressive bias)**, **1080p**, **1440p**, **4K**
- **Max video bitrate** slider to prefer smaller files (uses yt-dlp `tbr` as a selector hint)
- **Audio bitrate preference**:
  - Used as a *minimum* when selecting the audio stream (e.g., “≥192 kbps”)
  - For **MP3 export**, also used as the target encode bitrate (e.g., `192K`)
- Optional **Re-encode** (FFmpeg) to force a target video bitrate after download
- **Android client fallback** option for videos that fail in normal mode
- Cookies support:
  - `cookies.txt`
  - Read cookies directly from a browser profile folder
- **Threaded downloads**: GUI stays responsive while working
- **Cancel** button: stops at the next safe progress update

---

## Requirements

- **Python 3.10+**
- Python packages:
  - `yt-dlp`
  - `customtkinter`
- **FFmpeg** (required for merging and any re-encode / audio export) citeturn3view0

---

## Install

### Windows

1) Install Python 3.10+ from python.org  
   - ✅ During install: **Add Python to PATH**

2) Install packages:
```bat
python -m pip install --upgrade pip
python -m pip install yt-dlp customtkinter
```

3) Install FFmpeg  
   - Recommended: add FFmpeg `bin` folder to **PATH**
   - Test:
```bat
ffmpeg -version
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y python3-pip python3-tk ffmpeg
python3 -m pip install --user yt-dlp customtkinter
ffmpeg -version
```

### macOS

- Install Python 3 (Homebrew or python.org)
- Install packages:
```bash
python3 -m pip install yt-dlp customtkinter
```
- Install FFmpeg:
```bash
brew install ffmpeg
ffmpeg -version
```

---

## Run

From the folder containing the script:

### Windows
```bat
python your_script_name.py
```

### macOS / Linux
```bash
python3 your_script_name.py
```

> If you’re using the updated version from this repo, the script is typically named something like
> `you_tube_yt_dlp_gui_v_2_threaded_fixed.py` (or similar). Use the actual filename you have.

---

## How to Use

1) Click **Save to…** and pick a destination folder  
2) Paste a YouTube URL  
3) Choose settings:
   - **Quality**
   - **Audio bitrate** (minimum preferred audio stream; also used for MP3 encode)
   - **Max video bitrate** slider  
     - `0` = Auto (no limit)
   - **Re-encode to this bitrate**  
     - If enabled, set the slider to a value **> 0** (otherwise it will error)
4) Optional: enable **If normal fails, also try Android client**
5) Optional: choose cookies mode (see below)
6) Click:
   - **Download** (MP4)
   - **To MP3** (audio-only)
   - **To WAV** (audio-only)
7) Watch the log + progress bar. When done, you’ll get a success message.

---

## Audio bitrate (what it really means)

### “Audio bitrate” dropdown
- The app prefers an audio stream that meets a minimum bitrate (e.g. `ba[abr>=192]`) and falls back to bestaudio if not available. citeturn2view0

### MP3 export quality
- When converting audio with FFmpeg, yt-dlp’s audio quality accepts either:
  - a value **0–10** for VBR (0 = best), **or**
  - a bitrate like **`128K`** citeturn3view0  
- This GUI uses:
  - **Auto → `0`** (best VBR),
  - **≥192 kbps → `192K`** (CBR target), etc.

---

## Cookies / Authentication

Use cookies if:
- a video is age-restricted,
- region blocked,
- or you can view it logged-in but anonymous mode fails.

### Option A: cookies.txt
- Export cookies in **Netscape cookies.txt** format
- Select it in the GUI (**Use cookies.txt**)

### Option B: Browser profile folder
- Choose your browser in the GUI
- Paste or browse to the **profile folder**
  - Tip: in Chromium browsers, open `chrome://version` / `edge://version` to find the “Profile Path”

---

## Troubleshooting

### “Merging / processing” fails
- FFmpeg isn’t installed or not found in PATH. citeturn3view0

### 1080p / 4K fails but low-res works
- Enable **Android client fallback**
- Try cookies
- Use **List formats** to see what YouTube offers for that specific video

### Re-encode is enabled but slider is 0
- Set a target bitrate (e.g. 5000 kbps). 0 means “Auto” and can’t be used as a forced encode target.

### Cancel doesn’t instantly stop
- yt-dlp downloads in chunks; Cancel triggers a stop at the next safe progress-hook update.

---

## Quick checklist

- [ ] Python 3.10+
- [ ] `pip install yt-dlp customtkinter`
- [ ] FFmpeg installed (`ffmpeg -version`)
- [ ] Run the script
- [ ] Pick Save folder → paste URL → Download
