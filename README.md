# Motuo Video App

## First Setup

Requirements:

- Python 3.12+
- Node.js LTS with npm
- PowerShell
- FFmpeg binaries in `tools/ffmpeg/bin`

FFmpeg setup:

Download FFmpeg from:

```text
https://www.ffmpeg.org/download.html
```

Put these files here:

```text
tools/ffmpeg/bin/ffmpeg.exe
tools/ffmpeg/bin/ffprobe.exe
```

`ffplay.exe` is optional.

## Install Dependencies

From the project root:

```powershell
.\scripts\install.ps1
```

This creates `.venv`, installs Python dependencies, installs frontend dependencies, and builds the frontend.

## Run

```powershell
.\scripts\run.ps1
```

## Notes

- If FFmpeg is missing, video export falls back to less optimal behavior.
- For compatible MP4 cuts, keep `ffmpeg.exe` and `ffprobe.exe` in `tools/ffmpeg/bin`.
