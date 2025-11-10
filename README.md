# RTSP Timelapse

Connects to multiple RTSP camera streams, captures snapshots, and creates timelapse videos. Each camera saves its images in a dedicated folder organized by camera name.

## Features

- 📸 Capture single frames from multiple IP cameras via RTSP  
- 🎞️ Automatically create timelapse videos from captured images  
- 🗂️ Organized folder structure per camera (`input/{camera_name}/`)  
- 🕒 Timestamped image filenames  
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

### 3. Configure your cameras

Edit `config.py` and define your cameras:

```python
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

Check your camera’s documentation for the correct RTSP URL path.

---

## Usage

### 1. Capture frames

Capture snapshots from all configured cameras:

```bash
python3 main.py capture
```

Each camera’s images are saved to:

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

---

### 3. Automate with cron

You can schedule regular captures using cron.

Edit your crontab:

```bash
crontab -e
```

Add entries like:

```bash
# Capture at 8:00 AM
0 8 * * * cd /path/to/rtsp-timelapse && /usr/bin/python3 main.py capture >> /tmp/rtsp-timelapse.log 2>&1

# Capture at 4:30 PM
30 16 * * * cd /path/to/rtsp-timelapse && /usr/bin/python3 main.py capture >> /tmp/rtsp-timelapse.log 2>&1
```

Replace `/path/to/rtsp-timelapse` with your actual project path.

---

### 4. View logs

```bash
tail -f /tmp/rtsp-timelapse.log
```

---

## Project Structure

```
rtsp-timelapse/
├── config.py           # Camera configuration
├── main.py             # Main capture + timelapse script
├── input/              # Captured images (per camera)
│   ├── backyard/
│   └── sideyard/
├── output/             # Generated timelapse videos
└── README.md
```

--
## License

MIT License  
Copyright © 2025
