import os, sys, math, textwrap
from pathlib import Path
from urllib.parse import urlparse

import customtkinter as ctk
from tkinter import filedialog, messagebox

import yt_dlp as ydl

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

QUALITIES = ["Best (auto)","720p progressive bias","1080p","1440p","2160p (4K)"]

# NEW: Audio bitrate choices (minimum preferred bitrate for bestaudio)
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

# Map display label -> yt-dlp audio selector chunk
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

FMT_STRINGS = {
    # Note: This single-file progressive bias path does not apply the audio bitrate filter,
    # because it prefers progressive MP4s when available. We still keep it as a fallback path.
    "Best (auto)": "bestvideo*+bestaudio/best",
}

TARGET_HEIGHT = {"1080p":1080, "1440p":1440, "2160p (4K)":2160}

BROWSERS = ["chrome","edge","opera","brave","vivaldi","chromium","firefox"]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube → MP4 (yt-dlp ProfilePath GUI v2)")
        self.geometry("980x720")
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

        # URL
        ctk.CTkLabel(self, text="YouTube URL:", font=("Arial", 14)).grid(row=0, column=0, sticky="w", padx=16, pady=(16,6))
        self.url_entry = ctk.CTkEntry(self, width=930, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.grid(row=1, column=0, padx=16, sticky="ew")
        self.url_entry.bind("<Return>", lambda _ : self.start())

        # Save
        row = ctk.CTkFrame(self); row.grid(row=2, column=0, padx=16, pady=(10,0), sticky="ew"); row.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(row, text="Save to…", command=self.pick_dir, width=120).grid(row=0, column=0, padx=(0,8))
        self.dir_label = ctk.CTkLabel(row, text="No folder selected", anchor="w"); self.dir_label.grid(row=0, column=1, sticky="ew")

        # Quality + Android + Audio bitrate + Video bitrate slider
        row2 = ctk.CTkFrame(self); row2.grid(row=3, column=0, padx=16, pady=(10,0), sticky="ew")
        ctk.CTkLabel(row2, text="Quality:").grid(row=0, column=0, padx=(0,8))
        self.q = ctk.StringVar(value="Best (auto)")
        ctk.CTkOptionMenu(row2, variable=self.q, values=QUALITIES, width=220).grid(row=0, column=1, padx=(0,14))

        ctk.CTkLabel(row2, text="Audio bitrate:").grid(row=0, column=2, padx=(0,8))
        self.abr_pref = ctk.StringVar(value="Auto")
        ctk.CTkOptionMenu(row2, variable=self.abr_pref, values=AUDIO_BITRATES, width=180).grid(row=0, column=3, padx=(0,14))

        # NEW: Max video bitrate slider (0 = Auto/unlimited). Units are kbps; yt-dlp's tbr is in kbps.
        ctk.CTkLabel(row2, text="Max video bitrate:").grid(row=0, column=4, padx=(0,8))
        self.vbr_limit = ctk.IntVar(value=0)
        self.vbr_label = ctk.CTkLabel(row2, text="Auto")
        self.vbr_label.grid(row=0, column=5, padx=(0,8))
        self.vbr_slider = ctk.CTkSlider(row2, from_=0, to=MAX_VBR_KBPS, number_of_steps=250, command=self._on_vbr_change, width=200)
        self.vbr_slider.set(0)
        self.vbr_slider.grid(row=0, column=6, padx=(0,14))

        ctk.CTkCheckBox(row2, text="If normal fails, also try Android client", variable=self.try_android_after).grid(row=1, column=0, columnspan=4, sticky="w", pady=(6,0))

        # Re-encode toggle (uses the same slider value as the target encode bitrate)
        self.reencode = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(row2, text="Re-encode to this bitrate (FFmpeg)", variable=self.reencode, command=self._on_reencode_toggle).grid(row=1, column=4, columnspan=3, sticky="w", pady=(6,0))

        # Auth
        auth = ctk.CTkFrame(self); auth.grid(row=4, column=0, padx=16, pady=(12,0), sticky="ew")
        auth.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(auth, text="Authentication (choose one):", font=("Arial", 13)).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,6))
        ctk.CTkRadioButton(auth, text="No cookies (anonymous)", variable=self.auth_mode, value="none").grid(row=1, column=0, sticky="w")

        ctk.CTkRadioButton(auth, text="Use cookies.txt", variable=self.auth_mode, value="txt").grid(row=2, column=0, sticky="w")
        self.txt_label = ctk.CTkLabel(auth, text="No file chosen", anchor="w")
        self.txt_label.grid(row=2, column=1, sticky="ew", padx=(8,8))
        ctk.CTkButton(auth, text="Choose…", width=110, command=self.pick_cookies).grid(row=2, column=2)

        ctk.CTkRadioButton(auth, text="Use cookies from browser (point to a profile folder)", variable=self.auth_mode, value="browser").grid(row=3, column=0, sticky="w")
        self.browser_menu = ctk.CTkOptionMenu(auth, variable=self.browser_var, values=BROWSERS, width=160)
        self.browser_menu.grid(row=3, column=1, sticky="w", padx=(8,8))
        self.prof_entry = ctk.CTkEntry(auth, textvariable=self.profile_path, width=500, placeholder_text=r"Profile path (e.g., C:\Users\you\AppData\Local\Google\Chrome\User Data\Default)")
        self.prof_entry.grid(row=4, column=0, columnspan=2, sticky="ew", padx=(0,8), pady=(6,6))
        ctk.CTkButton(auth, text="Browse folder…", width=140, command=self.pick_profile_folder).grid(row=4, column=2)

        ctk.CTkLabel(self, text="Tip: In your browser, open chrome://version (or edge://version / opera://about) to copy the Profile Path.", text_color="#bdbdbd").grid(row=5, column=0, padx=16, pady=(6,0), sticky="w")

        # Controls
        row3 = ctk.CTkFrame(self); row3.grid(row=6, column=0, padx=16, pady=(14,0), sticky="ew"); row3.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(row3, text="Download", command=self.start).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(row3, text="List formats", command=self.list_formats).grid(row=0, column=1, padx=(10,0))
        ctk.CTkButton(row3, text="Open Folder", command=self.open_folder).grid(row=0, column=2, padx=(10,0))

        # Progress + log
        log = ctk.CTkFrame(self); log.grid(row=7, column=0, padx=16, pady=(12,16), sticky="nsew"); log.grid_columnconfigure(0, weight=1); log.grid_rowconfigure(1, weight=1)
        self.p = ctk.CTkProgressBar(log); self.p.configure(mode="determinate"); self.p.set(0); self.p.grid(row=0, column=0, sticky="ew")
        self.status = ctk.CTkTextbox(log, height=260); self.status.grid(row=1, column=0, sticky="nsew", pady=(8,0))
        self.log("Idle.")

    # Helpers
    def log(self, text):
        self.status.insert("end", f"{text}\n")
        self.status.see("end")

    def pick_dir(self):
        d = filedialog.askdirectory()
        if d: self.save_dir = d; self.dir_label.configure(text=d)

    def open_folder(self):
        if not self.save_dir:
            messagebox.showinfo("Open Folder", "Choose a save location first."); return
        try:
            if os.name=="nt": os.startfile(self.save_dir)  # type: ignore
            elif sys.platform=="darwin": os.system(f'open "{self.save_dir}"')
            else: os.system(f'xdg-open "{self.save_dir}"')
        except Exception as e: messagebox.showerror("Open Folder", str(e))

    def pick_cookies(self):
        p = filedialog.askopenfilename(title="Select cookies.txt (Netscape format)", filetypes=[("cookies.txt","*.txt"),("All files","*.*")])
        if p: self.cookies_file=p; self.txt_label.configure(text=os.path.basename(p)); self.auth_mode.set("txt")

    def pick_profile_folder(self):
        p = filedialog.askdirectory(title="Select browser profile folder")
        if p: self.profile_path.set(p); self.auth_mode.set("browser")

    def _auth_opts(self):
        mode = self.auth_mode.get()
        if mode=="txt":
            if not self.cookies_file or not Path(self.cookies_file).exists():
                raise RuntimeError("Pick a valid cookies.txt file.")
            return {"cookies": self.cookies_file}
        elif mode=="browser":
            prof = self.profile_path.get().strip() or None
            return {"cookiesfrombrowser": (self.browser_var.get(), prof, None, None)}
        else:
            return {}

    def _base_opts(self, outtmpl):
        return {
            "outtmpl": outtmpl,
            "noplaylist": True,
            "merge_output_format": "mp4",
            # postprocessors are set later depending on whether re-encode is enabled
            "progress_hooks": [self._hook],
            "quiet": True, "no_warnings": True,
            "retries": 10, "fragment_retries": 10,
            "http_chunk_size": 256*1024,
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

    def _try_download(self, url, fmt, client, auth_extra):
        outtmpl = os.path.join(self.save_dir, "%(title)s.%(ext)s")
        opts = self._base_opts(outtmpl)
        opts["format"] = fmt
        if client == "android":
            opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
        opts.update(auth_extra)

        # Choose remux vs re-encode
        if self.reencode.get():
            target = int(self.vbr_limit.get() or 0)
            if target <= 0:
                raise RuntimeError("Set a target bitrate (>0 kbps) when re-encode is enabled.")
            # Use the VideoConvertor PP and pass ffmpeg args
            opts["postprocessors"] = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
            # Keep audio as-is (copy) while re-encoding video to target bitrate
            ff_args = [
                "-c:v", "libx264",
                "-b:v", f"{target}k",
                "-maxrate", f"{target}k",
                "-bufsize", f"{target*2}k",
                "-pix_fmt", "yuv420p",
                "-preset", "medium",
                "-movflags", "+faststart",
                "-c:a", "copy",
            ]
            opts["postprocessor_args"] = ff_args
        else:
            # just remux to mp4 without re-encoding
            opts["postprocessors"] = [{"key":"FFmpegVideoRemuxer","preferedformat":"mp4"}]

        self.log(f"→ Trying format: {fmt} (client={client or 'normal'})")
        with ydl.YoutubeDL(opts) as Y:
            Y.download([url])

    def _audio_selector(self):
        """Return the bestaudio selector string based on UI preference."""
        label = self.abr_pref.get()
        return ABR_FILTERS.get(label, "ba")

    def _vbr_filter(self):
        """Return a yt-dlp filter like [tbr<=X] for video bitrate, or '' for Auto.
        tbr is in kbps and is available on most formats (separate video streams included)."""
        v = int(self.vbr_limit.get() or 0)
        return f"[tbr<={v}]" if v > 0 else ""

    def _height_attempts(self, target_h, audio_sel, vfilt):
        # Prefer separate video+audio with requested audio bitrate, then fallback to single-file at target height
        exact = f"bv*[height={target_h}]{vfilt}+{audio_sel}/b[height={target_h}]{vfilt}"
        leq = f"bv*[height<={target_h}]{vfilt}+{audio_sel}/b[height<={target_h}]{vfilt}"
        return [exact, leq]

    def _fmt_720_with_vbr(self, vfilt):
        # Progressive bias path @<=720p, apply tbr filter if set
        return f"best[height<=720][ext=mp4]{vfilt}/best[height<=720]{vfilt}"

    def start(self):
        url = self.url_entry.get().strip()
        if not url or "youtu" not in (urlparse(url).netloc or "").lower(): messagebox.showerror("Error","Enter a valid YouTube URL"); return
        if not self.save_dir: messagebox.showerror("Error","Choose a save folder"); return

        # Build attempt list
        attempts = []
        q = self.q.get()
        audio_sel = self._audio_selector()
        vfilt = self._vbr_filter()

        if q == "Best (auto)":
            # Apply audio + video bitrate preferences to the separate streams path; keep plain 'best' as fallback
            attempts.append(f"bestvideo*{vfilt}+{audio_sel}/best{vfilt}")
        elif q == "720p progressive bias":
            attempts.append(self._fmt_720_with_vbr(vfilt))
        else:
            target_h = TARGET_HEIGHT[q]
            attempts.extend(self._height_attempts(target_h, audio_sel, vfilt))

        clients = [None, "android"] if self.try_android_after.get() else [None]
        auth = {}
        try:
            auth = self._auth_opts()
        except Exception as e:
            messagebox.showerror("Error", str(e)); return

        # Try
        errors = []
        for client in clients:
            for fmt in attempts:
                try:
                    self._try_download(url, fmt, client, auth)
                    self.p.set(1.0); messagebox.showinfo("Success","Download complete."); return
                except Exception as e:
                    msg = str(e)
                    errors.append(f"[{client or 'normal'}] {fmt} → {msg}")
                    self.log(f"ERROR: {msg}")

        # If all failed, show last errors
        joined = "\n\n".join(errors[-6:]) if errors else "Unknown error"
        messagebox.showerror("Error", f"All strategies failed. Last errors:\n\n{joined}")

    def list_formats(self):
        url = self.url_entry.get().strip()
        if not url or "youtu" not in (urlparse(url).netloc or "").lower():
            messagebox.showerror("Error","Enter a valid YouTube URL"); return
        try:
            auth = self._auth_opts()
        except Exception as e:
            messagebox.showerror("Error", str(e)); return

        base = self._base_opts("%(title)s.%(ext)s")
        base.update(auth)
        info = None
        # Try normal then Android for listing
        for client in [None, "android"]:
            try:
                opts = dict(base)
                if client=="android":
                    opts["extractor_args"] = {"youtube":{"player_client":["android"]}}
                with ydl.YoutubeDL(opts) as Y:
                    info = Y.extract_info(url, download=False)
                used_client = client or "normal"
                break
            except Exception as e:
                self.log(f"List formats failed on {client or 'normal'}: {e}")
                continue
        if not info:
            messagebox.showerror("Error", "Could not fetch format list with provided auth."); return

        rows = []
        for f in (info.get("formats") or []):
            if not f.get("format_id"): continue
            h = f.get("height") or ""
            fps = f.get("fps") or ""
            v = f.get("vcodec") or ""
            a = f.get("acodec") or ""
            ext = f.get("ext") or ""
            abr = f.get("abr") or ""
            tbr = f.get("tbr") or ""
            rows.append(f"{f['format_id']:>6} | {ext:>4} | h={str(h):>4} | fps={str(fps):>3} | v={v[:12]:<12} | a={a[:9]:<9} | abr={str(abr):>4} | tbr={str(tbr):>5}")

        self.status.delete("1.0","end")
        self.log(f"Available formats ({used_client} client):")
        for r in rows:
            self.log(r)
        self.log("-- end of list --")

    def _hook(self, d):
        if d.get("status")=="downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            frac = (done/total) if total else 0.0
            self.p.set(frac)
            spd = d.get("speed"); eta = d.get("eta")
            txt = f"Downloading… {frac*100:.0f}%"
            if spd: txt += f" @ {spd/1024/1024:.2f} MB/s"
            if eta: txt += f" | ETA {eta}s"
            self.log(txt)
        elif d.get("status")=="finished":
            self.log("Merging / processing…")

if __name__=="__main__":
    app = App()
    app.mainloop()
