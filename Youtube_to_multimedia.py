import os
import sys
import math
import textwrap
import threading
import time
import queue
from pathlib import Path
from urllib.parse import urlparse

import customtkinter as ctk
from tkinter import filedialog, messagebox

import yt_dlp as ydl

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

QUALITIES = ["Best (auto)", "720p progressive bias", "1080p", "1440p", "2160p (4K)"]

# Audio bitrate choices (minimum preferred bitrate for selecting bestaudio)
AUDIO_BITRATES = [
    "Auto",
    "≥64 kbps",
    "≥96 kbps",
    "≥128 kbps",
    "≥160 kbps",
    "≥192 kbps",
    "≥256 kbps",
    "≥320 kbps",
]

# Map display label -> yt-dlp audio selector chunk (primary selector only)
ABR_FILTERS = {
    "Auto": "ba",
    "≥64 kbps": "ba[abr>=64]",
    "≥96 kbps": "ba[abr>=96]",
    "≥128 kbps": "ba[abr>=128]",
    "≥160 kbps": "ba[abr>=160]",
    "≥192 kbps": "ba[abr>=192]",
    "≥256 kbps": "ba[abr>=256]",
    "≥320 kbps": "ba[abr>=320]",
}

# Max slider value (in kbps) for video bitrate filter
MAX_VBR_KBPS = 25000  # 25 Mbps

TARGET_HEIGHT = {"1080p": 1080, "1440p": 1440, "2160p (4K)": 2160}

BROWSERS = ["chrome", "edge", "opera", "brave", "vivaldi", "chromium", "firefox"]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube → MP4/Audio (yt-dlp ProfilePath GUI v2)")
        self.geometry("980x760")
        self.resizable(True, True)

        # Make root grid expand with window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

        self.save_dir = None
        self.cookies_file = None
        self.auth_mode = ctk.StringVar(value="none")  # none|txt|browser
        self.browser_var = ctk.StringVar(value=BROWSERS[0])
        self.profile_path = ctk.StringVar(value="")
        self.try_android_after = ctk.BooleanVar(value=True)  # try Android after normal fails

        # Threading / UI queue
        self._ui_q = queue.Queue()
        self._busy = False
        self._worker = None
        self._cancel = threading.Event()
        self._hook_last_ts = 0.0
        self._last_pct_logged = -1
        self.after(100, self._drain_ui_queue)

        # URL
        ctk.CTkLabel(self, text="YouTube URL:", font=("Arial", 14)).grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 6)
        )
        self.url_entry = ctk.CTkEntry(self, width=930, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.grid(row=1, column=0, padx=16, sticky="ew")
        self.url_entry.bind("<Return>", lambda _: self.start())

        # Save
        row = ctk.CTkFrame(self)
        row.grid(row=2, column=0, padx=16, pady=(10, 0), sticky="ew")
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(row, text="Save to…", command=self.pick_dir, width=120).grid(
            row=0, column=0, padx=(0, 8)
        )
        self.dir_label = ctk.CTkLabel(row, text="No folder selected", anchor="w")
        self.dir_label.grid(row=0, column=1, sticky="ew")

        # Quality + Android + Audio bitrate + Video bitrate slider
        row2 = ctk.CTkFrame(self)
        row2.grid(row=3, column=0, padx=16, pady=(10, 0), sticky="ew")
        ctk.CTkLabel(row2, text="Quality:").grid(row=0, column=0, padx=(0, 8))
        self.q = ctk.StringVar(value="Best (auto)")
        ctk.CTkOptionMenu(row2, variable=self.q, values=QUALITIES, width=220).grid(
            row=0, column=1, padx=(0, 14)
        )

        ctk.CTkLabel(row2, text="Audio bitrate:").grid(row=0, column=2, padx=(0, 8))
        self.abr_pref = ctk.StringVar(value="Auto")
        ctk.CTkOptionMenu(row2, variable=self.abr_pref, values=AUDIO_BITRATES, width=180).grid(
            row=0, column=3, padx=(0, 14)
        )

        # Max video bitrate slider (0 = Auto/unlimited). Units are kbps; yt-dlp's tbr is in kbps.
        ctk.CTkLabel(row2, text="Max video bitrate:").grid(row=0, column=4, padx=(0, 8))
        self.vbr_limit = ctk.IntVar(value=0)
        self.vbr_label = ctk.CTkLabel(row2, text="Auto")
        self.vbr_label.grid(row=0, column=5, padx=(0, 8))
        self.vbr_slider = ctk.CTkSlider(
            row2,
            from_=0,
            to=MAX_VBR_KBPS,
            number_of_steps=250,
            command=self._on_vbr_change,
            width=200,
        )
        self.vbr_slider.set(0)
        self.vbr_slider.grid(row=0, column=6, padx=(0, 14))

        ctk.CTkCheckBox(
            row2,
            text="If normal fails, also try Android client",
            variable=self.try_android_after,
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))

        # Re-encode toggle (uses the same slider value as the target encode bitrate)
        self.reencode = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            row2,
            text="Re-encode to this bitrate (FFmpeg)",
            variable=self.reencode,
            command=self._on_reencode_toggle,
        ).grid(row=1, column=4, columnspan=3, sticky="w", pady=(6, 0))

        # Auth
        auth = ctk.CTkFrame(self)
        auth.grid(row=4, column=0, padx=16, pady=(12, 0), sticky="ew")
        auth.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(auth, text="Authentication (choose one):", font=("Arial", 13)).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        ctk.CTkRadioButton(auth, text="No cookies (anonymous)", variable=self.auth_mode, value="none").grid(
            row=1, column=0, sticky="w"
        )

        ctk.CTkRadioButton(auth, text="Use cookies.txt", variable=self.auth_mode, value="txt").grid(
            row=2, column=0, sticky="w"
        )
        self.txt_label = ctk.CTkLabel(auth, text="No file chosen", anchor="w")
        self.txt_label.grid(row=2, column=1, sticky="ew", padx=(8, 8))
        ctk.CTkButton(auth, text="Choose…", width=110, command=self.pick_cookies).grid(row=2, column=2)

        ctk.CTkRadioButton(
            auth,
            text="Use cookies from browser (point to a profile folder)",
            variable=self.auth_mode,
            value="browser",
        ).grid(row=3, column=0, sticky="w")
        self.browser_menu = ctk.CTkOptionMenu(auth, variable=self.browser_var, values=BROWSERS, width=160)
        self.browser_menu.grid(row=3, column=1, sticky="w", padx=(8, 8))
        self.prof_entry = ctk.CTkEntry(
            auth,
            textvariable=self.profile_path,
            width=500,
            placeholder_text=r"Profile path (e.g., C:\Users\you\AppData\Local\Google\Chrome\User Data\Default)",
        )
        self.prof_entry.grid(row=4, column=0, columnspan=2, sticky="ew", padx=(0, 8), pady=(6, 6))
        ctk.CTkButton(auth, text="Browse folder…", width=140, command=self.pick_profile_folder).grid(
            row=4, column=2
        )

        ctk.CTkLabel(
            self,
            text="Tip: In your browser, open chrome://version (or edge://version / opera://about) to copy the Profile Path.",
            text_color="#bdbdbd",
        ).grid(row=5, column=0, padx=16, pady=(6, 0), sticky="w")

        # Controls
        row3 = ctk.CTkFrame(self)
        row3.grid(row=6, column=0, padx=16, pady=(14, 0), sticky="ew")
        row3.grid_columnconfigure(0, weight=1)

        self.btn_download = ctk.CTkButton(row3, text="Download", command=self.start)
        self.btn_download.grid(row=0, column=0, sticky="w")

        self.btn_list = ctk.CTkButton(row3, text="List formats", command=self.list_formats)
        self.btn_list.grid(row=0, column=1, padx=(10, 0))

        self.btn_open = ctk.CTkButton(row3, text="Open Folder", command=self.open_folder)
        self.btn_open.grid(row=0, column=2, padx=(10, 0))

        # Audio-only convenience buttons
        self.btn_mp3 = ctk.CTkButton(row3, text="To MP3", command=self.to_mp3)
        self.btn_mp3.grid(row=0, column=3, padx=(10, 0))

        self.btn_wav = ctk.CTkButton(row3, text="To WAV", command=self.to_wav)
        self.btn_wav.grid(row=0, column=4, padx=(10, 0))

        self.btn_cancel = ctk.CTkButton(row3, text="Cancel", command=self.cancel, fg_color="#444444")
        self.btn_cancel.grid(row=0, column=5, padx=(10, 0))

        # Progress + log
        log = ctk.CTkFrame(self)
        log.grid(row=7, column=0, padx=16, pady=(12, 16), sticky="nsew")
        log.grid_columnconfigure(0, weight=1)
        log.grid_rowconfigure(1, weight=1)

        self.p = ctk.CTkProgressBar(log)
        self.p.configure(mode="determinate")
        self.p.set(0)
        self.p.grid(row=0, column=0, sticky="ew")

        self.status = ctk.CTkTextbox(log, height=300)
        self.status.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self.log("Idle.")

    # ---------------- UI helpers (thread-safe) ----------------
    def _ui(self, kind: str, *payload):
        """Enqueue a UI action to be handled on the Tk main thread."""
        self._ui_q.put((kind, payload))

    def _drain_ui_queue(self):
        try:
            while True:
                kind, payload = self._ui_q.get_nowait()

                if kind == "log":
                    (text,) = payload
                    self._log_direct(text)
                elif kind == "clear_log":
                    self.status.delete("1.0", "end")
                elif kind == "progress":
                    (frac,) = payload
                    self.p.set(max(0.0, min(1.0, float(frac))))
                elif kind == "msgbox":
                    level, title, msg = payload
                    if level == "info":
                        messagebox.showinfo(title, msg)
                    elif level == "warn":
                        messagebox.showwarning(title, msg)
                    else:
                        messagebox.showerror(title, msg)
                elif kind == "busy":
                    (is_busy,) = payload
                    self._set_busy_direct(bool(is_busy))
                else:
                    # Unknown event: ignore
                    pass

        except queue.Empty:
            pass

        self.after(100, self._drain_ui_queue)

    def _log_direct(self, text: str):
        self.status.insert("end", f"{text}\n")
        self.status.see("end")

    def log(self, text: str):
        self._ui("log", text)

    def ui_info(self, title: str, msg: str):
        self._ui("msgbox", "info", title, msg)

    def ui_warn(self, title: str, msg: str):
        self._ui("msgbox", "warn", title, msg)

    def ui_error(self, title: str, msg: str):
        self._ui("msgbox", "error", title, msg)

    def _set_busy_direct(self, is_busy: bool):
        self._busy = is_busy
        # disable action buttons while a job is running
        state = "disabled" if is_busy else "normal"
        for btn in (self.btn_download, self.btn_list, self.btn_mp3, self.btn_wav):
            btn.configure(state=state)
        self.btn_cancel.configure(state="normal" if is_busy else "disabled")

    # ---------------- Thread control ----------------
    def _start_job(self, target, *args, **kwargs):
        if self._busy:
            self.ui_warn("Busy", "A job is already running.")
            return
        self._cancel.clear()
        self._hook_last_ts = 0.0
        self._last_pct_logged = -1
        self._ui("progress", 0.0)
        self._ui("busy", True)

        def runner():
            try:
                target(*args, **kwargs)
            except Exception as e:
                # Make sure unexpected exceptions are visible.
                self.log(f"ERROR: {e}")
                self.ui_error("Error", str(e))
            finally:
                self._ui("busy", False)

        self._worker = threading.Thread(target=runner, daemon=True)
        self._worker.start()

    def cancel(self):
        if not self._busy:
            return
        self._cancel.set()
        self.log("Cancel requested… (will stop at next safe point)")

    # ---------------- GUI callbacks ----------------
    def pick_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.save_dir = d
            self.dir_label.configure(text=d)

    def open_folder(self):
        if not self.save_dir:
            self.ui_info("Open Folder", "Choose a save location first.")
            return
        try:
            if os.name == "nt":
                os.startfile(self.save_dir)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                os.system(f'open "{self.save_dir}"')
            else:
                os.system(f'xdg-open "{self.save_dir}"')
        except Exception as e:
            self.ui_error("Open Folder", str(e))

    def pick_cookies(self):
        p = filedialog.askopenfilename(
            title="Select cookies.txt (Netscape format)",
            filetypes=[("cookies.txt", "*.txt"), ("All files", "*.*")],
        )
        if p:
            self.cookies_file = p
            self.txt_label.configure(text=os.path.basename(p))
            self.auth_mode.set("txt")

    def pick_profile_folder(self):
        p = filedialog.askdirectory(title="Select browser profile folder")
        if p:
            self.profile_path.set(p)
            self.auth_mode.set("browser")

    # ---------------- yt-dlp option builders ----------------
    def _auth_opts(self):
        mode = self.auth_mode.get()
        if mode == "txt":
            if not self.cookies_file or not Path(self.cookies_file).exists():
                raise RuntimeError("Pick a valid cookies.txt file.")
            return {"cookies": self.cookies_file}
        if mode == "browser":
            prof = self.profile_path.get().strip() or None
            return {"cookiesfrombrowser": (self.browser_var.get(), prof, None, None)}
        return {}

    def _base_opts(self, outtmpl):
        return {
            "outtmpl": outtmpl,
            "noplaylist": True,
            "merge_output_format": "mp4",
            "progress_hooks": [self._hook],
            "quiet": True,
            "no_warnings": True,
            "retries": 10,
            "fragment_retries": 10,
            "http_chunk_size": 256 * 1024,
            "concurrent_fragment_downloads": 1,
        }

    def _on_vbr_change(self, val):
        val = int(val)
        self.vbr_limit.set(val)
        self._update_vbr_label()

    def _on_reencode_toggle(self):
        self._update_vbr_label()

    def _update_vbr_label(self):
        val = int(self.vbr_limit.get() or 0)
        if self.reencode.get():
            if val <= 0:
                self.vbr_label.configure(text="set >0 kbps")
            else:
                self.vbr_label.configure(text=f"≈ {val} kbps (encode)")
        else:
            if val <= 0:
                self.vbr_label.configure(text="Auto")
            else:
                self.vbr_label.configure(text=f"≤ {val} kbps")

    def _audio_primary(self):
        """Return the primary bestaudio selector string based on UI preference."""
        label = self.abr_pref.get()
        return ABR_FILTERS.get(label, "ba")

    def _vbr_filter(self):
        """Return a yt-dlp filter like [tbr<=X] for video bitrate, or '' for Auto.
        tbr is in kbps and is available on most formats (separate video streams included)."""
        v = int(self.vbr_limit.get() or 0)
        return f"[tbr<={v}]" if v > 0 else ""

    def _height_attempts(self, target_h: int, audio_primary: str, vfilt: str):
        # Prefer separate video+audio, then fallback to a combined format at that height
        v_exact = f"bv*[height={target_h}]{vfilt}"
        v_leq = f"bv*[height<={target_h}]{vfilt}"

        if audio_primary != "ba":
            exact = f"({v_exact}+{audio_primary})/({v_exact}+ba)/b[height={target_h}]{vfilt}"
            leq = f"({v_leq}+{audio_primary})/({v_leq}+ba)/b[height<={target_h}]{vfilt}"
        else:
            exact = f"{v_exact}+ba/b[height={target_h}]{vfilt}"
            leq = f"{v_leq}+ba/b[height<={target_h}]{vfilt}"
        return [exact, leq]

    def _fmt_720_with_vbr(self, vfilt: str):
        # Progressive bias path @<=720p, apply tbr filter if set
        return f"best[height<=720][ext=mp4]{vfilt}/best[height<=720]{vfilt}"

    # ---------------- Audio-only helpers ----------------
    def _preferred_quality_from_ui(self):
        """Return yt-dlp/FFmpegExtractAudio preferredquality based on UI.

        yt-dlp's --audio-quality accepts either:
        - a VBR quality number from 0 (best) to 10 (worst), or
        - an explicit bitrate like 128K (CBR/ABR depending on codec/ffmpeg).
        """
        label = self.abr_pref.get() or "Auto"
        if label == "Auto":
            return "0"  # best VBR quality
        digits = "".join(ch for ch in label if ch.isdigit())
        return f"{digits}K" if digits else "0"

    # ---------------- yt-dlp runners ----------------
    def _try_download(self, url, fmt, client, auth_extra, *, reencode: bool, target_kbps: int):
        outtmpl = os.path.join(self.save_dir, "%(title)s.%(ext)s")
        opts = self._base_opts(outtmpl)
        opts["format"] = fmt
        if client == "android":
            opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
        opts.update(auth_extra)

        # Choose remux vs re-encode
        if reencode:
            if target_kbps <= 0:
                raise RuntimeError("Set a target bitrate (>0 kbps) when re-encode is enabled.")
            opts["postprocessors"] = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
            # Keep audio as-is (copy) while re-encoding video to target bitrate
            ff_args = [
                "-c:v", "libx264",
                "-b:v", f"{target_kbps}k",
                "-maxrate", f"{target_kbps}k",
                "-bufsize", f"{target_kbps * 2}k",
                "-pix_fmt", "yuv420p",
                "-preset", "medium",
                "-movflags", "+faststart",
                "-c:a", "copy",
            ]
            opts["postprocessor_args"] = ff_args
        else:
            opts["postprocessors"] = [{"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}]

        self.log(f"→ Trying format: {fmt} (client={client or 'normal'})")
        with ydl.YoutubeDL(opts) as Y:
            Y.download([url])

    def _try_audio(self, url, fmt, codec, client, auth_extra, pref_q):
        outtmpl = os.path.join(self.save_dir, "%(title)s.%(ext)s")
        opts = self._base_opts(outtmpl)
        # For audio-only we don't want to force a video merge format
        opts["merge_output_format"] = None
        opts["format"] = fmt
        if client == "android":
            opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
        opts.update(auth_extra)
        # Extract & convert to desired audio codec
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
                "preferredquality": pref_q,
            }
        ]

        self.log(f"→ Audio-only: {fmt} → {codec.upper()} (client={client or 'normal'})")
        with ydl.YoutubeDL(opts) as Y:
            Y.download([url])

    # ---------------- Actions (threaded) ----------------
    def start(self):
        """Download the URL as MP4 using the selected quality options."""
        url = self.url_entry.get().strip()
        if not url or "youtu" not in (urlparse(url).netloc or "").lower():
            self.ui_error("Error", "Enter a valid YouTube URL")
            return
        if not self.save_dir:
            self.ui_error("Error", "Choose a save folder")
            return
        try:
            auth = self._auth_opts()
        except Exception as e:
            self.ui_error("Error", str(e))
            return

        q = self.q.get()
        audio_primary = self._audio_primary()
        vfilt = self._vbr_filter()

        attempts = []
        if q == "Best (auto)":
            v = f"bestvideo*{vfilt}"
            if audio_primary != "ba":
                attempts.append(f"({v}+{audio_primary})/({v}+ba)/best{vfilt}")
            else:
                attempts.append(f"{v}+ba/best{vfilt}")
        elif q == "720p progressive bias":
            attempts.append(self._fmt_720_with_vbr(vfilt))
        else:
            target_h = TARGET_HEIGHT[q]
            attempts.extend(self._height_attempts(target_h, audio_primary, vfilt))

        clients = [None, "android"] if self.try_android_after.get() else [None]
        reencode = bool(self.reencode.get())
        target_kbps = int(self.vbr_limit.get() or 0)

        self._start_job(self._download_worker, url, attempts, clients, auth, reencode, target_kbps)

    def _download_worker(self, url, attempts, clients, auth, reencode, target_kbps):
        errors = []
        for client in clients:
            for fmt in attempts:
                if self._cancel.is_set():
                    raise RuntimeError("Cancelled")
                try:
                    self._try_download(
                        url,
                        fmt,
                        client,
                        auth,
                        reencode=reencode,
                        target_kbps=target_kbps,
                    )
                    self._ui("progress", 1.0)
                    self.ui_info("Success", "Download complete.")
                    return
                except Exception as e:
                    msg = str(e)
                    errors.append(f"[{client or 'normal'}] {fmt} → {msg}")
                    self.log(f"ERROR: {msg}")

        joined = "\n\n".join(errors[-6:]) if errors else "Unknown error"
        self.ui_error("Error", f"All strategies failed. Last errors:\n\n{joined}")

    def to_mp3(self):
        """Download & convert the URL to MP3 using FFmpegExtractAudio."""
        url = self.url_entry.get().strip()
        if not url or "youtu" not in (urlparse(url).netloc or "").lower():
            self.ui_error("Error", "Enter a valid YouTube URL")
            return
        if not self.save_dir:
            self.ui_error("Error", "Choose a save folder")
            return
        try:
            auth = self._auth_opts()
        except Exception as e:
            self.ui_error("Error", str(e))
            return

        audio_primary = self._audio_primary()
        fmt = f"{audio_primary}/ba" if audio_primary != "ba" else "ba"
        pref_q = self._preferred_quality_from_ui()
        clients = [None, "android"] if self.try_android_after.get() else [None]

        self._start_job(self._audio_worker, url, fmt, "mp3", clients, auth, pref_q)

    def to_wav(self):
        """Download & convert the URL to WAV using FFmpegExtractAudio."""
        url = self.url_entry.get().strip()
        if not url or "youtu" not in (urlparse(url).netloc or "").lower():
            self.ui_error("Error", "Enter a valid YouTube URL")
            return
        if not self.save_dir:
            self.ui_error("Error", "Choose a save folder")
            return
        try:
            auth = self._auth_opts()
        except Exception as e:
            self.ui_error("Error", str(e))
            return

        audio_primary = self._audio_primary()
        fmt = f"{audio_primary}/ba" if audio_primary != "ba" else "ba"
        clients = [None, "android"] if self.try_android_after.get() else [None]

        self._start_job(self._audio_worker, url, fmt, "wav", clients, auth, "0")

    def _audio_worker(self, url, fmt, codec, clients, auth, pref_q):
        errors = []
        for client in clients:
            if self._cancel.is_set():
                raise RuntimeError("Cancelled")
            try:
                self._try_audio(url, fmt, codec=codec, client=client, auth_extra=auth, pref_q=pref_q)
                self._ui("progress", 1.0)
                self.ui_info("Success", f"Saved as {codec.upper()}.")
                return
            except Exception as e:
                msg = str(e)
                errors.append(f"[{client or 'normal'}] {codec.upper()} → {msg}")
                self.log(f"ERROR: {msg}")

        joined = "\n\n".join(errors[-6:]) if errors else "Unknown error"
        self.ui_error("Error", f"{codec.upper()} extraction failed. Last errors:\n\n{joined}")

    def list_formats(self):
        url = self.url_entry.get().strip()
        if not url or "youtu" not in (urlparse(url).netloc or "").lower():
            self.ui_error("Error", "Enter a valid YouTube URL")
            return
        try:
            auth = self._auth_opts()
        except Exception as e:
            self.ui_error("Error", str(e))
            return

        self._start_job(self._list_formats_worker, url, auth)

    def _list_formats_worker(self, url, auth):
        base = self._base_opts("%(title)s.%(ext)s")
        base.update(auth)

        info = None
        used_client = "normal"

        for client in [None, "android"]:
            if self._cancel.is_set():
                raise RuntimeError("Cancelled")
            try:
                opts = dict(base)
                if client == "android":
                    opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
                with ydl.YoutubeDL(opts) as Y:
                    info = Y.extract_info(url, download=False)
                used_client = client or "normal"
                break
            except Exception as e:
                self.log(f"List formats failed on {client or 'normal'}: {e}")
                continue

        if not info:
            self.ui_error("Error", "Could not fetch format list with provided auth.")
            return

        rows = []
        for f in (info.get("formats") or []):
            if not f.get("format_id"):
                continue
            h = f.get("height") or ""
            fps = f.get("fps") or ""
            v = f.get("vcodec") or ""
            a = f.get("acodec") or ""
            ext = f.get("ext") or ""
            abr = f.get("abr") or ""
            tbr = f.get("tbr") or ""
            rows.append(
                f"{f['format_id']:>6} | {ext:>4} | h={str(h):>4} | fps={str(fps):>3} | "
                f"v={v[:12]:<12} | a={a[:9]:<9} | abr={str(abr):>4} | tbr={str(tbr):>5}"
            )

        self._ui("clear_log")
        self.log(f"Available formats ({used_client} client):")
        for r in rows:
            self.log(r)
        self.log("-- end of list --")

    def _hook(self, d):
        # Runs inside the downloader thread
        if self._cancel.is_set():
            raise RuntimeError("Cancelled")

        status = d.get("status")
        now = time.monotonic()

        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            frac = (done / total) if total else 0.0

            # Throttle UI updates
            if now - self._hook_last_ts >= 0.2:
                self._hook_last_ts = now
                self._ui("progress", frac)

                pct = int(frac * 100) if total else -1
                if pct != -1 and pct != self._last_pct_logged:
                    self._last_pct_logged = pct
                    spd = d.get("speed")
                    eta = d.get("eta")
                    txt = f"Downloading… {pct:d}%"
                    if spd:
                        txt += f" @ {spd / 1024 / 1024:.2f} MB/s"
                    if eta:
                        txt += f" | ETA {eta}s"
                    self.log(txt)

        elif status == "finished":
            self.log("Merging / processing…")


if __name__ == "__main__":
    app = App()
    app.mainloop()
