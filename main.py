import config
import os
import subprocess
from datetime import datetime


base_images_directory = "input"


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


def main():
    print(f"Taking pictures from all cameras...")
    
    # Capture frames from all configured cameras
    for camera in config.cameras:
        capture_camera_frame(camera)
    
    print("Capture complete!")


if __name__ == "__main__":
    main()
