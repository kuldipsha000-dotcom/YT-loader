# YouTube Downloader

A sleek, Python-based desktop application for downloading videos and audio from YouTube. Built with `tkinter` and powered by `yt-dlp`.

## Features

- **User-Friendly GUI**: Easy-to-use interface for pasting links and selecting download options.
- **Multiple Download Modes**: Choose between "Video + Audio", "Video Only", or "Audio Only".
- **Quality Selection**: Pick your desired resolution (Best, 1080p, 720p, 480p, 360p, 240p).
- **Live Progress Tracking**: Visual progress bar and percentage display for active downloads.
- **Video Preview**: Fetches and displays the video title and thumbnail before downloading.
- **Customizable Themes**: Supports "Dark", "Light", "Glass Dark", and "Glass Light" themes. You can also adjust the blur intensity for glass themes. Theme preferences are saved automatically.
- **Clipboard Support**: Easily paste YouTube links directly from your clipboard with a single click.

## Installation & Usage

### Option 1: For Non-Coders (Recommended)
You do not need to install Python or any code dependencies. 
Simply download the pre-compiled executable file and run it directly:
1. Download the zip folder from the **Releases** section.
2. Extract the contents of the zip folder.
3. Double-click the extracted `yt loader.exe` file to start the application.

### Option 2: For Developers (Run from Source)
If you prefer to run the application from the source code, make sure you have Python installed.

**Prerequisites:**
Install the required libraries:
```bash
pip install yt-dlp Pillow
```
*(Note: `tkinter` and `urllib` are included in the standard Python library).*

**How to Run:**
Navigate to the project directory and run the main script:
```bash
python "yt loader.py"
```

## How to Build Executable

The project includes a PyInstaller specification file (`yt loader.spec`) to bundle the application into a standalone executable.

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the executable:
   ```bash
   pyinstaller "yt loader.spec"
   ```
The compiled executable will be available in the `dist` folder.

## Files Structure

- `yt loader.py`: The main application script containing the GUI and download logic.
- `theme_config.json`: Stores user theme preferences (auto-generated).
- `yt loader.spec`: Configuration file for building the application with PyInstaller.
- `logo.ico.ico`: Icon file for the application.

---
**Developed by kuldip sha**
