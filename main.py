import config
import os
import subprocess
import argparse
import tempfile
import urllib.request
import urllib.parse
from datetime import datetime


base_images_directory = "./input"
output_directory = "output"


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def _telegram_send(msg):
    if not getattr(config, "telegram_enabled", False):
        return

    token = getattr(config, "telegram_bot_token", None)
    chat_id = getattr(config, "telegram_chat_id", None)

    if not token or not chat_id:
        return

    try:
        params = urllib.parse.urlencode(
            {
                "chat_id": chat_id,
                "text": f"[rtsp-timelapse] {msg}"
            }
        )

        urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage?{params}",
            timeout=10
        )

    except Exception as e:
        log(f"Failed to send Telegram notification: {e}")


def notify_error(msg):
    _telegram_send(msg)


def notify_capture(msg):
    if getattr(config, "telegram_notify_on_capture", False):
        _telegram_send(msg)


def notify_timelapse(msg):
    if getattr(config, "telegram_notify_on_timelapse", False):
        _telegram_send(msg)


def capture_camera_frame(camera):
    """
    Capture a single frame from a camera RTSP stream.
    """

    camera_name = camera["name"]
    camera_dir = f"{base_images_directory}/{camera_name}"

    # Create camera directory if it doesn't exist
    os.makedirs(camera_dir, exist_ok=True)

    # Build RTSP URL
    rtsp_url = (
        f"rtsp://{camera['username']}:{camera['password']}"
        f"@{camera['ip_address']}/{camera['rtsp_path']}"
    )

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"{camera_dir}/{timestamp}.png"

    log(f"Capturing frame from {camera_name} ({camera['ip_address']})")

    ffmpeg_command = [
        "ffmpeg",

        # Force TCP transport for RTSP stability
        "-rtsp_transport", "tcp",

        # Reduce ffmpeg console spam
        "-loglevel", "error",

        # Input stream
        "-i", rtsp_url,

        # Seek 1 second into stream
        "-ss", "00:00:01",

        # Capture only one frame
        "-frames:v", "1",

        # Output format
        "-f", "image2",

        # Overwrite output file
        "-y",

        # Output image
        output_file,
    ]

    try:
        result = subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True,
            check=True
        )

        log(f"Successfully captured frame to {output_file}")
        notify_capture(
            f"Frame captured: {camera_name} → {output_file}"
        )

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else str(e)

        msg = (
            f"Error capturing frame from "
            f"{camera_name}: {stderr}"
        )

        log(msg)
        notify_error(msg)


def create_timelapse(camera_name, framerate=5):
    """
    Create a timelapse video from captured images.
    """

    # Validate camera name
    valid_cameras = [cam["name"] for cam in config.cameras]

    if camera_name not in valid_cameras:
        msg = (
            f"Error: Camera '{camera_name}' not found in configuration. "
            f"Available: {', '.join(valid_cameras)}"
        )

        log(msg)
        notify_error(msg)
        return False

    camera_dir = f"{base_images_directory}/{camera_name}"

    # Check if camera directory exists
    if not os.path.exists(camera_dir):
        msg = (
            f"Error: No images found for camera "
            f"'{camera_name}' at {camera_dir}"
        )

        log(msg)
        notify_error(msg)
        return False

    all_files = sorted(
        f for f in os.listdir(camera_dir)
        if f.endswith(".png")
    )

    image_files = [
        f for f in all_files
        if os.path.getsize(f"{camera_dir}/{f}") > 0
    ]

    skipped = len(all_files) - len(image_files)

    if not image_files:
        msg = f"Error: No valid PNG images found in {camera_dir}"

        log(msg)
        notify_error(msg)
        return False

    log(
        f"Found {len(image_files)} images for camera "
        f"'{camera_name}'"
        + (
            f" ({skipped} empty files skipped)"
            if skipped else ""
        )
    )

    # Create output directory
    os.makedirs(output_directory, exist_ok=True)

    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    output_file = (
        f"{output_directory}/"
        f"{camera_name}_timelapse_{timestamp}.mp4"
    )

    log(f"Creating timelapse video at {framerate} fps...")

    concat_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False
        ) as f:

            for img in image_files:
                abs_path = os.path.abspath(
                    f"{camera_dir}/{img}"
                )

                f.write(f"file '{abs_path}'\n")

            concat_file = f.name

        ffmpeg_command = [
            "ffmpeg",

            "-loglevel", "error",

            "-f", "concat",
            "-safe", "0",

            "-r", str(framerate),

            "-i", concat_file,

            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",

            "-y",

            output_file,
        ]

        subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True,
            check=True
        )

        log(f"Successfully created timelapse: {output_file}")

        notify_timelapse(
            f"Timelapse created: "
            f"{camera_name} "
            f"({len(image_files)} frames) "
            f"→ {output_file}"
        )

        return True

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else str(e)

        msg = (
            f"Error creating timelapse for "
            f"'{camera_name}': {stderr}"
        )

        log(msg)
        notify_error(msg)

        return False

    finally:
        if concat_file and os.path.exists(concat_file):
            os.unlink(concat_file)


def capture_all_cameras():
    """
    Capture frames from all configured cameras.
    """

    log("Taking pictures from all cameras...")

    for camera in config.cameras:
        capture_camera_frame(camera)

    log("Capture complete!")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "RTSP Timelapse - "
            "Capture frames or create timelapse videos "
            "from IP cameras"
        ),

        formatter_class=argparse.RawDescriptionHelpFormatter,

        epilog="""
Examples:

  # Capture frames from all cameras
  python main.py capture

  # Create timelapse for a specific camera
  python main.py timelapse --camera backyard

  # Create timelapse with custom framerate
  python main.py timelapse --camera backyard --framerate 30
"""
    )

    parser.add_argument(
        "mode",
        choices=["capture", "timelapse"],
        help=(
            "Mode: "
            "'capture' to take snapshots, "
            "'timelapse' to create video"
        )
    )

    parser.add_argument(
        "--camera",
        type=str,
        help="Camera name (required for timelapse mode)"
    )

    parser.add_argument(
        "--framerate",
        type=int,
        default=24,
        help="Framerate for timelapse video (default: 24 fps)"
    )

    args = parser.parse_args()

    if args.mode == "capture":
        capture_all_cameras()

    elif args.mode == "timelapse":

        if not args.camera:
            parser.error(
                "timelapse mode requires --camera argument"
            )

        create_timelapse(
            args.camera,
            args.framerate
        )


if __name__ == "__main__":
    main()