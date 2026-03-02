import config
import os
import subprocess
import argparse
import tempfile
import urllib.request
import urllib.parse
from datetime import datetime


base_images_directory = "input"
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
        params = urllib.parse.urlencode({"chat_id": chat_id, "text": f"[rtsp-timelapse] {msg}"})
        urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage?{params}", timeout=10)
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
    Capture a single frame from a camera's RTSP stream.
    :param camera: Dictionary containing camera configuration
    """
    camera_name = camera["name"]
    camera_dir = f"{base_images_directory}/{camera_name}"
    
    # Create camera directory if it doesn't exist
    os.makedirs(camera_dir, exist_ok=True)
    
    # Build RTSP URL
    rtsp_url = f"rtsp://{camera['username']}:{camera['password']}@{camera['ip_address']}/{camera['rtsp_path']}"
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"{camera_dir}/{timestamp}.png"
    
    log(f"Capturing frame from {camera_name} ({camera['ip_address']})")

    # Use ffmpeg to connect to the RTSP stream and save 1 frame
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                rtsp_url,
                "-vframes",
                "1",
                "-y",  # Overwrite output file if it exists
                output_file,
            ],
            capture_output=True,
            check=True
        )
        log(f"Successfully captured frame to {output_file}")
        notify_capture(f"Frame captured: {camera_name} → {output_file}")
    except subprocess.CalledProcessError as e:
        msg = f"Error capturing frame from {camera_name}: {e}"
        log(msg)
        notify_error(msg)


def create_timelapse(camera_name, framerate=5):
    """
    Create a timelapse video from captured images for a specific camera.
    :param camera_name: Name of the camera to create timelapse for
    :param framerate: Frames per second for the output video (default: 24)
    """
    # Validate camera name
    valid_cameras = [cam["name"] for cam in config.cameras]
    if camera_name not in valid_cameras:
        msg = f"Error: Camera '{camera_name}' not found in configuration. Available: {', '.join(valid_cameras)}"
        log(msg)
        notify_error(msg)
        return False

    camera_dir = f"{base_images_directory}/{camera_name}"

    # Check if camera directory exists and has images
    if not os.path.exists(camera_dir):
        msg = f"Error: No images found for camera '{camera_name}' at {camera_dir}"
        log(msg)
        notify_error(msg)
        return False

    all_files = sorted(f for f in os.listdir(camera_dir) if f.endswith('.png'))
    image_files = [f for f in all_files if os.path.getsize(f"{camera_dir}/{f}") > 0]
    skipped = len(all_files) - len(image_files)

    if not image_files:
        msg = f"Error: No valid PNG images found in {camera_dir}"
        log(msg)
        notify_error(msg)
        return False

    log(f"Found {len(image_files)} images for camera '{camera_name}'" +
        (f" ({skipped} empty files skipped)" if skipped else ""))

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"{output_directory}/{camera_name}_timelapse_{timestamp}.mp4"

    log(f"Creating timelapse video at {framerate} fps...")

    # Use ffmpeg to create timelapse from images via concat list
    concat_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for img in image_files:
                f.write(f"file '{os.path.abspath(f'{camera_dir}/{img}')}'\n")
            concat_file = f.name

        subprocess.run(
            [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-r", str(framerate),
                "-i", concat_file,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-y",  # Overwrite output file if it exists
                output_file,
            ],
            capture_output=True,
            check=True
        )
        log(f"Successfully created timelapse: {output_file}")
        notify_timelapse(f"Timelapse created: {camera_name} ({len(image_files)} frames) → {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        msg = f"Error creating timelapse for '{camera_name}': {e.stderr.decode()}"
        log(msg)
        notify_error(msg)
        return False
    finally:
        if concat_file and os.path.exists(concat_file):
            os.unlink(concat_file)


def capture_all_cameras():
    """Capture frames from all configured cameras."""
    log("Taking pictures from all cameras...")
    for camera in config.cameras:
        capture_camera_frame(camera)
    log("Capture complete!")


def main():
    parser = argparse.ArgumentParser(
        description="RTSP Timelapse - Capture frames or create timelapse videos from IP cameras",
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
        help="Mode: 'capture' to take snapshots, 'timelapse' to create video"
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
            parser.error("timelapse mode requires --camera argument")
        create_timelapse(args.camera, args.framerate)


if __name__ == "__main__":
    main()
