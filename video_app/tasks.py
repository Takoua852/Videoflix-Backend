import os
import shutil
import subprocess
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def convert_resolutions(video_id: int, source_path: str):
    """
    Background task to convert a video into HLS (480p, 720p, 1080p).

    Uses FFmpeg with '-codec copy' for faster conversion without re-encoding.
    Deletes existing files for the video before starting.

    Args:
        video_id (int): ID of the Video object.
        source_path (str): Path to the source video file.
    """
    resolutions = ["480p", "720p", "1080p"]
    base_dir = os.path.join(settings.MEDIA_ROOT, "videos", str(video_id))

    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)

    for res in resolutions:
        output_dir = os.path.join(base_dir, res)
        os.makedirs(output_dir, exist_ok=True)
        playlist_path = os.path.join(output_dir, "index.m3u8")

        command = [
            "ffmpeg",
            "-i", source_path,
            "-codec", "copy",
            "-start_number", "0",
            "-hls_time", "10",
            "-hls_list_size", "0",
            "-f", "hls",
            playlist_path
        ]

        try:
            subprocess.run(command, check=True)
        except Exception as e:
            logger.error(f"HLS Conversion failed: {e}")