# RTSP Timelapse

Connects to multiple RTSP camera streams and captures snapshots for creating timelapses. Each camera saves images to its own folder, organized by camera name.

## Features
- Support for multiple IP cameras with individual credentials
- Each camera saves to a separate folder (`input/{camera_name}/`)
- Timestamped image captures
- Designed to run via cron for scheduled captures
- Lightweight - no external Python dependencies required

## Hardware Requirements
- A Linux machine (Raspberry Pi, Ubuntu server, etc.)
- One or more IP cameras that support RTSP streams

## Installation

### 1. Install ffmpeg
You need [ffmpeg](https://ffmpeg.org/) installed on your system:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 2. Clone or download this project
```bash
git clone <your-repo-url>
cd rtsp-timelapse
```

### 3. Configure your cameras
Edit `config.py` and add your camera details:
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

**Note:** The `rtsp_path` varies by camera manufacturer. Common paths include:
- `/stream1` or `/stream2`
- `/Streaming/Channels/101`
- `/cam/realmonitor?channel=1&subtype=0`

Check your camera's documentation for the correct RTSP path.

## Usage

### Manual capture
Run the script manually to capture images from all cameras:
```bash
python3 main.py
```

Images will be saved to:
- `input/backyard/YYYYMMDD-HHMMSS.png`
- `input/sideyard/YYYYMMDD-HHMMSS.png`

### Automated capture with cron
To capture images automatically at scheduled times, set up a cron job.

1. Open crontab editor:
```bash
crontab -e
```

2. Add entries for your desired schedule (example: 8:00 AM and 4:30 PM daily):
```bash
# Capture at 8:00 AM
0 8 * * * cd /path/to/rtsp-timelapse && /usr/bin/python3 main.py >> /tmp/rtsp-timelapse.log 2>&1

# Capture at 4:30 PM
30 16 * * * cd /path/to/rtsp-timelapse && /usr/bin/python3 main.py >> /tmp/rtsp-timelapse.log 2>&1
```

3. Replace `/path/to/rtsp-timelapse` with your actual project path

4. Save and exit

### View logs
Check the log file to troubleshoot issues:
```bash
tail -f /tmp/rtsp-timelapse.log
```

## Creating Timelapses

This script focuses on capturing images. To create timelapse videos from the captured images, you can use ffmpeg:

```bash
# Create timelapse from a camera's images
cd input/backyard
ffmpeg -framerate 24 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p output.mp4
```

Timelapse creation features will be added in future updates.

## Project Structure
```
rtsp-timelapse/
├── config.py           # Camera configuration
├── main.py            # Main capture script
├── input/             # Captured images (organized by camera)
│   ├── backyard/
│   └── sideyard/
├── output/            # For future timelapse videos
└── README.md
```

## Troubleshooting

**Images not capturing:**
- Verify camera IP addresses are correct
- Test RTSP URL manually: `ffplay rtsp://username:password@ip_address/path`
- Check camera credentials
- Ensure cameras are on the same network

**Cron job not running:**
- Check cron logs: `grep CRON /var/log/syslog`
- Verify script path is absolute in crontab
- Check file permissions: `chmod +x main.py`

## License
MIT
