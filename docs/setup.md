# Local Setup

Use this when you have the project source and want to run the app locally on Windows.

## Prerequisites

- Python 3.12+
- Node.js LTS
- PowerShell

`ffmpeg` is recommended for compatible MP4 exports. The installer script tries to install it with `winget` if it is missing. You can also place `ffmpeg.exe` and `ffprobe.exe` in:

```text
tools\ffmpeg\bin\
```

## Install

From the project root:

```powershell
.\scripts\install.ps1
```

To skip ffmpeg installation:

```powershell
.\scripts\install.ps1 -SkipFfmpeg
```

## Run

```powershell
.\scripts\run.ps1
```

## What The Installer Does

- Creates `.venv`
- Installs Python dependencies from `requirements.txt`
- Runs `npm install` in `frontend`
- Builds the frontend with `npm run build`
- Checks for `ffmpeg`
