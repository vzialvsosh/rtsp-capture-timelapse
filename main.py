import config
import os
import subprocess
import argparse
from datetime import datetime


base_images_directory = "input"
output_directory = "output"


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
    
    print(f"Capturing frame from {camera_name} ({camera['ip_address']})")
    
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
        print(f"Successfully captured frame to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error capturing frame from {camera_name}: {e}")


def create_timelapse(camera_name, framerate=10):
    """
    Create a timelapse video from captured images for a specific camera.
    :param camera_name: Name of the camera to create timelapse for
    :param framerate: Frames per second for the output video (default: 24)
    """
    # Validate camera name
    valid_cameras = [cam["name"] for cam in config.cameras]
    if camera_name not in valid_cameras:
        print(f"Error: Camera '{camera_name}' not found in configuration.")
        print(f"Available cameras: {', '.join(valid_cameras)}")
        return False
    
    camera_dir = f"{base_images_directory}/{camera_name}"
    
    # Check if camera directory exists and has images
    if not os.path.exists(camera_dir):
        print(f"Error: No images found for camera '{camera_name}' at {camera_dir}")
        return False
    
    image_files = [f for f in os.listdir(camera_dir) if f.endswith('.png')]
    if not image_files:
        print(f"Error: No PNG images found in {camera_dir}")
        return False
    
    print(f"Found {len(image_files)} images for camera '{camera_name}'")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"{output_directory}/{camera_name}_timelapse_{timestamp}.mp4"
    
    print(f"Creating timelapse video at {framerate} fps...")
    
    # Use ffmpeg to create timelapse from images
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-framerate", str(framerate),
                "-pattern_type", "glob",
                "-i", f"{camera_dir}/*.png",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-y",  # Overwrite output file if it exists
                output_file,
            ],
            capture_output=True,
            check=True
        )
        print(f"Successfully created timelapse: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating timelapse: {e}")
        print(f"stderr: {e.stderr.decode()}")
        return False


def capture_all_cameras():
    """Capture frames from all configured cameras."""
    print(f"Taking pictures from all cameras...")
    
    # Capture frames from all configured cameras
    for camera in config.cameras:
        capture_camera_frame(camera)
    
    print("Capture complete!")


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
