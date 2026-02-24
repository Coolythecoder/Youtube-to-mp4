# YouTube → MP4 / MP3 / WAV (CustomTkinter + yt-dlp)

A **desktop GUI** for downloading YouTube videos as **MP4** (video+audio merged) and exporting **audio-only** as **MP3** or **WAV** — with quality presets, bitrate controls, cookies support, and a threaded progress log.

This README matches the current script: `Youtube_to_multimedia.py`.

---

## Features

- **Download MP4** (video + audio, merged/remuxed to MP4)
- **Audio-only exports**
  - **To MP3**
  - **To WAV**
- **Quality presets**
  - Best (auto)
  - 720p progressive bias
  - 1080p / 1440p / 2160p (4K)
- **Audio bitrate preference**
  - Picks an audio stream meeting a *minimum* bitrate when possible (e.g. ≥192 kbps), otherwise falls back to best available
  - For **MP3 export**, the selection also drives the target encode quality/bitrate
- **Max video bitrate slider** (kbps)
  - `0` = Auto (no limit)
  - Uses yt-dlp’s `tbr` (total bitrate) as a format selector hint
- **Optional re-encode (FFmpeg)** to force a target video bitrate
  - Re-encodes video to H.264 (`libx264`) at the slider bitrate, copies audio
- **Authentication / cookies**
  - Anonymous (no cookies)
  - `cookies.txt` (Netscape format)
  - Read cookies from a browser profile folder (`cookiesfrombrowser`)
- **Fallback mode for stubborn videos**
  - If normal mode fails, it can also try **Android / iOS / TV** YouTube clients
- **List formats** button (prints available formats to the log)
- **Threaded downloads + Cancel** (GUI stays responsive)

---

## Requirements

### 1) Python
- **Python 3.10+** recommended

### 2) Python packages
Install via pip:
- `yt-dlp`
- `customtkinter`

### 3) FFmpeg (required)
FFmpeg is required for:
- merging/remuxing to MP4
- MP3/WAV export
- any re-encode

### 4) Deno (strongly recommended)
Recent yt-dlp YouTube support often relies on a **JS runtime**. This app will:
- auto-detect `deno` from PATH, or
- use `YTDLP_DENO_PATH` if set, or
- check the common install location `~/.deno/bin/deno`

If Deno is missing, yt-dlp may still work, but you may see more failures/missing formats.

### 5) Optional: `yt-dlp-ejs`
If `yt-dlp-ejs` isn’t installed, the script allows fetching EJS components remotely (more convenient, but depends on network access).

---

## Install

### Windows

1) Install Python (3.10+)
- During install: ✅ **Add Python to PATH**

2) Install packages:
```bat
python -m pip install --upgrade pip
python -m pip install yt-dlp customtkinter
```

3) Install FFmpeg
- Make sure `ffmpeg.exe` is on PATH
- Test:
```bat
ffmpeg -version
```

4) (Recommended) Install Deno
- Ensure `deno` is on PATH
- Test:
```bat
deno --version
```

---

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y python3-pip python3-tk ffmpeg
python3 -m pip install --user yt-dlp customtkinter

# Recommended:
# sudo apt install -y deno   (if available on your distro) OR install via Deno’s official method
ffmpeg -version
```

> `python3-tk` matters on Linux because the GUI uses Tkinter under the hood.

---

### macOS

```bash
python3 -m pip install --upgrade pip
python3 -m pip install yt-dlp customtkinter
brew install ffmpeg

# Recommended:
brew install deno
```

---

## Run

From the folder containing the script:

### Windows
```bat
python Youtube_to_multimedia.py
```

### macOS / Linux
```bash
python3 Youtube_to_multimedia.py
```

---

## How to use

1) Click **Save to…** and choose a destination folder  
2) Paste a YouTube URL  
3) Choose:
   - **Quality**
   - **Audio bitrate** (minimum preferred audio stream; also used for MP3 target quality)
   - **Max video bitrate** slider
4) Optional:
   - Enable **If normal fails, also try Android/iOS/TV clients**
   - Choose an **Authentication** mode (cookies)
   - Enable **Re-encode to this bitrate** (requires slider > 0)
5) Click:
   - **Download** (MP4)
   - **To MP3**
   - **To WAV**
   - **List formats** (debug/inspect available streams)
6) Watch the log + progress bar  
7) Use **Open Folder** to jump to your output directory

---

## Settings explained

### Quality
- **Best (auto)** tries best available video + best available audio
- **720p progressive bias** prefers single-file “progressive” formats up to 720p (often faster/simpler)
- **1080p / 1440p / 4K** targets that height (with fallbacks to “≤ height”)

### Audio bitrate
The dropdown is treated as a **minimum preferred** bitrate when selecting bestaudio:
- Example: “≥192 kbps” tries `ba[abr>=192]`, then falls back if unavailable.

For **MP3 export**, it also picks the encode target:
- Auto → best VBR mode
- ≥192 kbps → `192K`

### Max video bitrate slider
- `0` = Auto (no limit)
- Otherwise it adds a format filter like `[tbr<=X]` as a hint to pick smaller video streams.

### Re-encode to this bitrate (FFmpeg)
When enabled:
- The app re-encodes video to H.264 at your slider bitrate
- Audio is copied (not re-encoded)
- You must set slider **> 0**, otherwise it errors.

---

## Cookies / Authentication

Use cookies if:
- the video is age-restricted,
- region blocked,
- members-only,
- or it plays logged-in but fails anonymously.

### Option A: cookies.txt
1) Export cookies in **Netscape cookies.txt** format
2) In the app: select **Use cookies.txt** → **Choose…**

### Option B: Browser profile folder
1) Select your browser
2) Paste/browse to the **profile folder**
   - Tip (Chromium browsers): open `chrome://version` / `edge://version` / `opera://about` and copy the “Profile Path”

> If cookie import fails, try closing the browser first (some profiles lock cookie DB files).

---

## Troubleshooting

### “Merging / processing…” fails
- FFmpeg is missing or not on PATH.
- Verify:
```bash
ffmpeg -version
```

### 1080p / 4K fails but low-res works
Try, in order:
1) Enable **Android/iOS/TV client fallback**
2) Use cookies (browser profile or cookies.txt)
3) Use **List formats** to see what’s actually available for that video

### Re-encode enabled but slider is 0
- Set a target bitrate (e.g. **5000 kbps**).  
  `0` means “Auto” and can’t be used as a forced encode target.

### Cancel doesn’t stop instantly
- yt-dlp downloads in chunks. Cancel triggers a stop at the next safe progress-hook update.

### “Enter a valid YouTube URL”
- The app checks that the URL’s domain contains `youtu`. Make sure it’s a real YouTube link.

---

## Optional: build a Windows .exe (PyInstaller)

If you want a standalone executable:

```bat
python -m pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed Youtube_to_multimedia.py
```

The output will be in `dist\Youtube_to_multimedia.exe`.

**Notes:**
- You still need FFmpeg available (bundle it separately or ship with instructions).
- If you rely on Deno, users also need Deno or you need to bundle a runtime setup.

---

## Legal / usage note

You’re responsible for complying with YouTube’s Terms of Service and local laws. Use this tool for content you have the rights/permission to download.
