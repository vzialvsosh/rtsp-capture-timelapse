# RTSP Timelapse

Connects to multiple RTSP camera streams, captures snapshots, and creates timelapse videos. Each camera saves its images in a dedicated folder organized by camera name.

## Features

- 📸 Capture single frames from multiple IP cameras via RTSP
- 🎞️ Automatically create timelapse videos from captured images
- 🗂️ Organized folder structure per camera (`input/{camera_name}/`)
- 🕒 Timestamped log output and image filenames
- ⏭️ Skips empty/corrupt frames when building timelapse
- 🔔 Optional Telegram notifications for captures, timelapse completion, and errors
- ⚙️ Designed for scheduled runs via cron
- 💡 Lightweight — no external Python dependencies required (uses `ffmpeg`)

---

## Hardware Requirements

- A Linux-based system (e.g., Raspberry Pi, Ubuntu server, etc.)
- One or more IP cameras supporting RTSP streaming
- [ffmpeg](https://ffmpeg.org/) installed on your system

---

## Installation

### 1. Install ffmpeg

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 2. Clone this project

```bash
git clone https://github.com/m4ary/rtsp-capture-timelapse
cd rtsp-timelapse
```

### 3. Configure your cameras and notifications

Edit `config.py`:

```python
# Telegram notifications
telegram_enabled = False  # master switch — set to True to enable

telegram_bot_token = "your_bot_token"
telegram_chat_id = "your_chat_id"

telegram_notify_on_capture = False  # notify on each frame capture
telegram_notify_on_timelapse = True # notify when a timelapse is created

# Cameras
cameras = [
    {
        "name": "backyard",
        "ip_address": "192.168.4.10",
        "username": "admin",
        "password": "your_password",
        "rtsp_path": "/Streaming/Channels/101"
    },
    {
        "name": "sideyard",
        "ip_address": "192.168.4.16",
        "username": "admin",
        "password": "your_password",
        "rtsp_path": "/Streaming/Channels/101"
    }
]
```

**Note:** The RTSP path varies by camera manufacturer.
Common examples:
- `/stream1`, `/stream2`
- `/Streaming/Channels/101`
- `/cam/realmonitor?channel=1&subtype=0`

Check your camera's documentation for the correct RTSP URL path.

---

## Telegram Notifications

To receive Telegram alerts:

1. Create a bot via [@BotFather](https://t.me/BotFather) and copy the token
2. Get your chat ID (e.g. via [@userinfobot](https://t.me/userinfobot))
3. Set them in `config.py` and set `telegram_enabled = True`

| Config key | Default | Description |
|---|---|---|
| `telegram_enabled` | `False` | Master switch for all notifications |
| `telegram_bot_token` | `None` | Bot token from BotFather |
| `telegram_chat_id` | `None` | Your Telegram chat/user ID |
| `telegram_notify_on_capture` | `False` | Notify on each successful frame capture |
| `telegram_notify_on_timelapse` | `True` | Notify when a timelapse video is created |

Errors (capture failure, ffmpeg error, missing camera) always trigger a notification when `telegram_enabled = True`, regardless of the per-event flags.

---

## Usage

### 1. Capture frames

Capture snapshots from all configured cameras:

```bash
python3 main.py capture
```

Each camera's images are saved to:

```
input/{camera_name}/YYYYMMDD-HHMMSS.png
```

---

### 2. Create timelapse videos

Create a timelapse video from saved images for a specific camera:

```bash
python3 main.py timelapse --camera backyard
```

To specify a custom frame rate (e.g., 30 fps):

```bash
python3 main.py timelapse --camera backyard --framerate 30
```

Output videos are saved to:

```
output/{camera_name}_timelapse_{timestamp}.mp4
```

Example:
```
output/backyard_timelapse_20251111-090000.mp4
```

Empty or corrupt image files (e.g. from a camera that was offline) are automatically skipped. The log will report how many were skipped:

```
[2026-01-26 07:00:01] Found 118 images for camera 'backyard' (8 empty files skipped)
```

---

### 3. Automate with cron

Edit your crontab:

```bash
crontab -e
```

Add entries like:

```bash
# Capture at 7:00 AM every day
0 7 * * * cd /path/to/rtsp-timelapse && /usr/bin/python3 main.py capture >> /tmp/rtsp-timelapse.log 2>&1

# Create timelapse for backyard every Sunday at midnight
0 0 * * 0 cd /path/to/rtsp-timelapse && /usr/bin/python3 main.py timelapse --camera backyard >> /tmp/rtsp-timelapse.log 2>&1
```

Replace `/path/to/rtsp-timelapse` with your actual project path.

---

### 4. View logs

All output is timestamped:

```
[2026-03-01 07:00:01] Taking pictures from all cameras...
[2026-03-01 07:00:02] Capturing frame from backyard (192.168.4.10)
[2026-03-01 07:00:03] Successfully captured frame to input/backyard/20260301-070003.png
```

```bash
tail -f /tmp/rtsp-timelapse.log
```

---

## Project Structure

```
rtsp-timelapse/
├── config.py           # Camera and notification configuration
├── main.py             # Main capture + timelapse script
├── input/              # Captured images (per camera)
│   ├── backyard/
│   └── sideyard/
├── output/             # Generated timelapse videos
└── README.md
```

---

## License

MIT License
Copyright © 2025
