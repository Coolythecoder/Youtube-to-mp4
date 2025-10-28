YouTube Downloader GUI Setup Guide

=================================



-------------------------------------------------

0\. WHAT THIS APP DOES

-------------------------------------------------

This is a YouTube to MP4 downloader with a graphical window (no command line needed once it's running).



Main features:

\- Paste a YouTube link and download the video as MP4.

\- Pick video quality (720p / 1080p / 1440p / 4K / Best).

\- Set max video bitrate to keep file sizes smaller.

\- Pick minimum audio bitrate (128 kbps, 192 kbps, etc).

\- Optional re-encode step using FFmpeg to force a target bitrate.

\- Save to any folder you choose.

\- Option to try "Android client" mode for blocked videos.

\- Support for cookies (for age-restricted/private videos).



The script uses:

\- Python (for the app code + GUI)

\- yt-dlp (actually downloads the video and audio)

\- FFmpeg (merges audio+video and can re-encode)





-------------------------------------------------

1\. WHAT YOU NEED BEFORE RUNNING

-------------------------------------------------



You need these three things:



1\) Python 3.10 or newer

&nbsp;  - On Windows: install from python.org

&nbsp;  - On Linux/macOS: usually already there



2\) Python packages

&nbsp;  - yt-dlp

&nbsp;  - customtkinter

&nbsp;  (You will install these with pip)



3\) FFmpeg

&nbsp;  - Used to merge audio + video

&nbsp;  - Used to compress the final MP4 to a custom bitrate





-------------------------------------------------

2\. WINDOWS SETUP (STEP BY STEP)

-------------------------------------------------



STEP 1. Install Python

----------------------

1\. Download Python for Windows from python.org (any 3.x is fine, 3.10+).

2\. Run the installer.

3\. IMPORTANT: tick "Add Python to PATH".

4\. Click "Install Now".



To check it worked:

\- Open Command Prompt

\- Type:

&nbsp; python --version

You should see something like: Python 3.12.x

(If that fails, try: py --version)



STEP 2. Install required Python packages

----------------------------------------

In Command Prompt, run:

&nbsp; python -m pip install yt-dlp customtkinter



This installs:

\- yt-dlp (the downloader)

\- customtkinter (the dark themed GUI toolkit)



If you get "pip is not recognized", close and reopen Command Prompt and try again.



STEP 3. Install FFmpeg

----------------------

Option A (recommended):

1\. Download a Windows build of FFmpeg.

2\. Extract it. Inside the 'bin' folder you will see ffmpeg.exe.

3\. Add that 'bin' folder to PATH:

&nbsp;  - Press Windows key, search "environment variables".

&nbsp;  - Click "Edit the system environment variables".

&nbsp;  - Click "Environment Variables...".

&nbsp;  - Under "System variables", select "Path", click Edit.

&nbsp;  - Click New, paste the path to your FFmpeg 'bin' folder. OK, OK.



To test:

&nbsp; ffmpeg -version

If you see version info, it worked.



Option B (quick and dirty):

\- Put ffmpeg.exe (and ffprobe.exe, ffplay.exe if you have them)

&nbsp; in the SAME folder as the script

&nbsp; (example: C:\\yt-dlp-gui\\)



STEP 4. Put the script somewhere

--------------------------------

Make a folder, for example:

&nbsp; C:\\yt-dlp-gui\\

Put:

&nbsp; YouTube\_yt\_dlp\_GUI\_v2\_resizable.py

there.



STEP 5. Run the program

-----------------------

In Command Prompt:

&nbsp; cd C:\\yt-dlp-gui

&nbsp; python YouTube\_yt\_dlp\_GUI\_v2\_resizable.py



If everything is OK, a window will pop up with:

\- URL box

\- "Save to..." button

\- Quality / bitrate options

\- Download button

\- Progress bar and log box





-------------------------------------------------

3\. LINUX (UBUNTU / DEBIAN STYLE)

-------------------------------------------------



STEP 1. Check Python and pip

----------------------------

Run:

&nbsp; python3 --version

You want 3.10 or newer.



Install pip and Tk support if needed:

&nbsp; sudo apt update

&nbsp; sudo apt install -y python3-pip python3-tk



STEP 2. Install Python packages

-------------------------------

Run:

&nbsp; python3 -m pip install --user yt-dlp customtkinter



STEP 3. Install FFmpeg

----------------------

Run:

&nbsp; sudo apt install -y ffmpeg

&nbsp; ffmpeg -version

You should see version info.



STEP 4. Run the program

-----------------------

1\. Put the script somewhere, e.g.:

&nbsp;  ~/yt-dlp-gui/YouTube\_yt\_dlp\_GUI\_v2\_resizable.py

2\. Then:

&nbsp;  cd ~/yt-dlp-gui

&nbsp;  python3 YouTube\_yt\_dlp\_GUI\_v2\_resizable.py



If you're on a desktop session (not SSH only), the GUI should appear.

If you get errors about "\_tkinter" or display, install python3-tk (above)

and make sure you’re running it in a normal graphical session.





-------------------------------------------------

4\. macOS SETUP

-------------------------------------------------



STEP 1. Install Python 3

------------------------

If you have Homebrew:

&nbsp; brew install python3

Then check:

&nbsp; python3 --version



NOTE:

If you get GUI errors later about tkinter,

install Python from python.org instead. The python.org build

includes Tcl/Tk support which the GUI needs.



STEP 2. Install packages

------------------------

Run:

&nbsp; python3 -m pip install yt-dlp customtkinter



STEP 3. Install FFmpeg

----------------------

If you have Homebrew:

&nbsp; brew install ffmpeg

Then test:

&nbsp; ffmpeg -version



STEP 4. Run the program

-----------------------

Put the script somewhere like:

&nbsp; ~/yt-dlp-gui/YouTube\_yt\_dlp\_GUI\_v2\_resizable.py



Then:

&nbsp; cd ~/yt-dlp-gui

&nbsp; python3 YouTube\_yt\_dlp\_GUI\_v2\_resizable.py



The window should open.





-------------------------------------------------

5\. HOW TO USE THE APP (ONCE IT'S OPEN)

-------------------------------------------------



1\. Click "Save to..." and choose where you want the MP4 to go.

&nbsp;  (This MUST be set or it won't know where to save.)



2\. Paste a YouTube link into the URL box.

&nbsp;  Example:

&nbsp;  https://www.youtube.com/watch?v=dQw4w9WgXcQ



3\. Pick your settings:

&nbsp;  - Quality (Best / 720p / 1080p / 1440p / 4K)

&nbsp;  - Minimum audio bitrate (like >=192 kbps)

&nbsp;  - Max video bitrate slider

&nbsp;    - 0 = Auto (no limit)

&nbsp;    - Any other number = try not to pick video above that kbps

&nbsp;  - Re-encode checkbox

&nbsp;    - If you tick this, it will run FFmpeg after download

&nbsp;      to force the bitrate you chose. This makes files smaller.

&nbsp;    - IMPORTANT: If you enable re-encode,

&nbsp;      set a number on the slider. Leaving it at 0 will fail.



4\. "If normal fails, also try Android client"

&nbsp;  - YouTube sometimes blocks higher quality unless you're logged in.

&nbsp;  - Enabling this lets yt-dlp pretend to be an Android YouTube app.

&nbsp;  - This can help with age/region restrictions.



5\. Cookies section:

&nbsp;  - "No cookies (anonymous)" works for most public videos.

&nbsp;  - "Use cookies.txt" lets you load exported cookies for age-locked videos.

&nbsp;  - "Use cookies from browser" = point it at your browser profile folder

&nbsp;    (for example Chrome's Default profile on Windows).

&nbsp;  - This is helpful for age-restricted or private videos you actually

&nbsp;    have access to in your browser.



6\. Click "Download".

&nbsp;  - The progress bar will update.

&nbsp;  - The log box at the bottom will show details.

&nbsp;  - FFmpeg will merge audio+video and (if enabled) re-encode.



7\. When it's done, you get a success message.

&nbsp;  Your MP4 will be in the folder you picked.





-------------------------------------------------

6\. COMMON PROBLEMS AND FIXES

-------------------------------------------------



A) Error: ModuleNotFoundError: No module named 'customtkinter'

&nbsp;  Fix: You ran Python without installing the packages.

&nbsp;  Command:

&nbsp;    python -m pip install customtkinter yt-dlp

&nbsp;  (Use python3 on Linux/macOS.)



B) It downloads, then errors during "Merging / processing"

&nbsp;  Fix: FFmpeg is missing or not in PATH.

&nbsp;  Install FFmpeg and make sure "ffmpeg -version" works.



C) GUI won't launch on Linux, complains about \_tkinter or display

&nbsp;  Fix:

&nbsp;    sudo apt install -y python3-tk

&nbsp;  Also: run it in a normal desktop session, not just over SSH.



D) 1080p / 4K fails but 360p works

&nbsp;  Fix ideas:

&nbsp;  - Tick "If normal fails, also try Android client".

&nbsp;  - Use cookies (age/region block).

&nbsp;  - Click "List formats" to see what YouTube is actually offering

&nbsp;    for that video.



E) Re-encode enabled but bitrate slider is 0

&nbsp;  Fix:

&nbsp;  - Choose a number like 5000 kbps first. 0 means "no limit",

&nbsp;    which conflicts with "force re-encode" mode.





-------------------------------------------------

7\. QUICK CHECKLIST (TL;DR)

-------------------------------------------------



\[ ] Python 3 installed (and added to PATH on Windows)

\[ ] pip install yt-dlp customtkinter

\[ ] FFmpeg installed and working (ffmpeg -version succeeds)

\[ ] Run the script with python / python3

\[ ] Pick Save folder, paste link, choose quality

\[ ] Hit Download

\[ ] Enjoy your MP4

YouTube Downloader GUI Setup Guide

=================================



-------------------------------------------------

0\. WHAT THIS APP DOES

-------------------------------------------------

This is a YouTube to MP4 downloader with a graphical window (no command line needed once it's running).



Main features:

\- Paste a YouTube link and download the video as MP4.

\- Pick video quality (720p / 1080p / 1440p / 4K / Best).

\- Set max video bitrate to keep file sizes smaller.

\- Pick minimum audio bitrate (128 kbps, 192 kbps, etc).

\- Optional re-encode step using FFmpeg to force a target bitrate.

\- Save to any folder you choose.

\- Option to try "Android client" mode for blocked videos.

\- Support for cookies (for age-restricted/private videos).



The script uses:

\- Python (for the app code + GUI)

\- yt-dlp (actually downloads the video and audio)

\- FFmpeg (merges audio+video and can re-encode)





-------------------------------------------------

1\. WHAT YOU NEED BEFORE RUNNING

-------------------------------------------------



You need these three things:



1\) Python 3.10 or newer

&nbsp;  - On Windows: install from python.org

&nbsp;  - On Linux/macOS: usually already there



2\) Python packages

&nbsp;  - yt-dlp

&nbsp;  - customtkinter

&nbsp;  (You will install these with pip)



3\) FFmpeg

&nbsp;  - Used to merge audio + video

&nbsp;  - Used to compress the final MP4 to a custom bitrate





-------------------------------------------------

2\. WINDOWS SETUP (STEP BY STEP)

-------------------------------------------------



STEP 1. Install Python

----------------------

1\. Download Python for Windows from python.org (any 3.x is fine, 3.10+).

2\. Run the installer.

3\. IMPORTANT: tick "Add Python to PATH".

4\. Click "Install Now".



To check it worked:

\- Open Command Prompt

\- Type:

&nbsp; python --version

You should see something like: Python 3.12.x

(If that fails, try: py --version)



STEP 2. Install required Python packages

----------------------------------------

In Command Prompt, run:

&nbsp; python -m pip install yt-dlp customtkinter



This installs:

\- yt-dlp (the downloader)

\- customtkinter (the dark themed GUI toolkit)



If you get "pip is not recognized", close and reopen Command Prompt and try again.



STEP 3. Install FFmpeg

----------------------

Option A (recommended):

1\. Download a Windows build of FFmpeg.

2\. Extract it. Inside the 'bin' folder you will see ffmpeg.exe.

3\. Add that 'bin' folder to PATH:

&nbsp;  - Press Windows key, search "environment variables".

&nbsp;  - Click "Edit the system environment variables".

&nbsp;  - Click "Environment Variables...".

&nbsp;  - Under "System variables", select "Path", click Edit.

&nbsp;  - Click New, paste the path to your FFmpeg 'bin' folder. OK, OK.



To test:

&nbsp; ffmpeg -version

If you see version info, it worked.



Option B (quick and dirty):

\- Put ffmpeg.exe (and ffprobe.exe, ffplay.exe if you have them)

&nbsp; in the SAME folder as the script

&nbsp; (example: C:\\yt-dlp-gui\\)



STEP 4. Put the script somewhere

--------------------------------

Make a folder, for example:

&nbsp; C:\\yt-dlp-gui\\

Put:

&nbsp; YouTube\_yt\_dlp\_GUI\_v2\_resizable.py

there.



STEP 5. Run the program

-----------------------

In Command Prompt:

&nbsp; cd C:\\yt-dlp-gui

&nbsp; python YouTube\_yt\_dlp\_GUI\_v2\_resizable.py



If everything is OK, a window will pop up with:

\- URL box

\- "Save to..." button

\- Quality / bitrate options

\- Download button

\- Progress bar and log box





-------------------------------------------------

3\. LINUX (UBUNTU / DEBIAN STYLE)

-------------------------------------------------



STEP 1. Check Python and pip

----------------------------

Run:

&nbsp; python3 --version

You want 3.10 or newer.



Install pip and Tk support if needed:

&nbsp; sudo apt update

&nbsp; sudo apt install -y python3-pip python3-tk



STEP 2. Install Python packages

-------------------------------

Run:

&nbsp; python3 -m pip install --user yt-dlp customtkinter



STEP 3. Install FFmpeg

----------------------

Run:

&nbsp; sudo apt install -y ffmpeg

&nbsp; ffmpeg -version

You should see version info.



STEP 4. Run the program

-----------------------

1\. Put the script somewhere, e.g.:

&nbsp;  ~/yt-dlp-gui/YouTube\_yt\_dlp\_GUI\_v2\_resizable.py

2\. Then:

&nbsp;  cd ~/yt-dlp-gui

&nbsp;  python3 YouTube\_yt\_dlp\_GUI\_v2\_resizable.py



If you're on a desktop session (not SSH only), the GUI should appear.

If you get errors about "\_tkinter" or display, install python3-tk (above)

and make sure you’re running it in a normal graphical session.





-------------------------------------------------

4\. macOS SETUP

-------------------------------------------------



STEP 1. Install Python 3

------------------------

If you have Homebrew:

&nbsp; brew install python3

Then check:

&nbsp; python3 --version



NOTE:

If you get GUI errors later about tkinter,

install Python from python.org instead. The python.org build

includes Tcl/Tk support which the GUI needs.



STEP 2. Install packages

------------------------

Run:

&nbsp; python3 -m pip install yt-dlp customtkinter



STEP 3. Install FFmpeg

----------------------

If you have Homebrew:

&nbsp; brew install ffmpeg

Then test:

&nbsp; ffmpeg -version



STEP 4. Run the program

-----------------------

Put the script somewhere like:

&nbsp; ~/yt-dlp-gui/YouTube\_yt\_dlp\_GUI\_v2\_resizable.py



Then:

&nbsp; cd ~/yt-dlp-gui

&nbsp; python3 YouTube\_yt\_dlp\_GUI\_v2\_resizable.py



The window should open.





-------------------------------------------------

5\. HOW TO USE THE APP (ONCE IT'S OPEN)

-------------------------------------------------



1\. Click "Save to..." and choose where you want the MP4 to go.

&nbsp;  (This MUST be set or it won't know where to save.)



2\. Paste a YouTube link into the URL box.

&nbsp;  Example:

&nbsp;  https://www.youtube.com/watch?v=dQw4w9WgXcQ



3\. Pick your settings:

&nbsp;  - Quality (Best / 720p / 1080p / 1440p / 4K)

&nbsp;  - Minimum audio bitrate (like >=192 kbps)

&nbsp;  - Max video bitrate slider

&nbsp;    - 0 = Auto (no limit)

&nbsp;    - Any other number = try not to pick video above that kbps

&nbsp;  - Re-encode checkbox

&nbsp;    - If you tick this, it will run FFmpeg after download

&nbsp;      to force the bitrate you chose. This makes files smaller.

&nbsp;    - IMPORTANT: If you enable re-encode,

&nbsp;      set a number on the slider. Leaving it at 0 will fail.



4\. "If normal fails, also try Android client"

&nbsp;  - YouTube sometimes blocks higher quality unless you're logged in.

&nbsp;  - Enabling this lets yt-dlp pretend to be an Android YouTube app.

&nbsp;  - This can help with age/region restrictions.



5\. Cookies section:

&nbsp;  - "No cookies (anonymous)" works for most public videos.

&nbsp;  - "Use cookies.txt" lets you load exported cookies for age-locked videos.

&nbsp;  - "Use cookies from browser" = point it at your browser profile folder

&nbsp;    (for example Chrome's Default profile on Windows).

&nbsp;  - This is helpful for age-restricted or private videos you actually

&nbsp;    have access to in your browser.



6\. Click "Download".

&nbsp;  - The progress bar will update.

&nbsp;  - The log box at the bottom will show details.

&nbsp;  - FFmpeg will merge audio+video and (if enabled) re-encode.



7\. When it's done, you get a success message.

&nbsp;  Your MP4 will be in the folder you picked.





-------------------------------------------------

6\. COMMON PROBLEMS AND FIXES

-------------------------------------------------



A) Error: ModuleNotFoundError: No module named 'customtkinter'

&nbsp;  Fix: You ran Python without installing the packages.

&nbsp;  Command:

&nbsp;    python -m pip install customtkinter yt-dlp

&nbsp;  (Use python3 on Linux/macOS.)



B) It downloads, then errors during "Merging / processing"

&nbsp;  Fix: FFmpeg is missing or not in PATH.

&nbsp;  Install FFmpeg and make sure "ffmpeg -version" works.



C) GUI won't launch on Linux, complains about \_tkinter or display

&nbsp;  Fix:

&nbsp;    sudo apt install -y python3-tk

&nbsp;  Also: run it in a normal desktop session, not just over SSH.



D) 1080p / 4K fails but 360p works

&nbsp;  Fix ideas:

&nbsp;  - Tick "If normal fails, also try Android client".

&nbsp;  - Use cookies (age/region block).

&nbsp;  - Click "List formats" to see what YouTube is actually offering

&nbsp;    for that video.



E) Re-encode enabled but bitrate slider is 0

&nbsp;  Fix:

&nbsp;  - Choose a number like 5000 kbps first. 0 means "no limit",

&nbsp;    which conflicts with "force re-encode" mode.





-------------------------------------------------

7\. QUICK CHECKLIST (TL;DR)

-------------------------------------------------



\[ ] Python 3 installed (and added to PATH on Windows)

\[ ] pip install yt-dlp customtkinter

\[ ] FFmpeg installed and working (ffmpeg -version succeeds)

\[ ] Run the script with python / python3

\[ ] Pick Save folder, paste link, choose quality

\[ ] Hit Download

\[ ] Enjoy your MP4



