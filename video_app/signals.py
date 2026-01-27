from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import Video
from .tasks import convert_resolutions
import django_rq
from django.conf import settings
import shutil
import os

@receiver(post_save, sender=Video)
def process_video_on_upload(sender, instance, created, **kwargs):
    """Trigger HLS transcoding as a background task whenever a new video is uploaded."""
    if created and instance.source:
        queue = django_rq.get_queue("default", autocommit=True)
        queue.enqueue(convert_resolutions, instance.id, instance.source.path)


@receiver(post_delete, sender=Video)
def cleanup_video_files(sender, instance, **kwargs):
    """Delete the video source, thumbnail, and all generated HLS files when a Video instance is deleted."""
    for file in [instance.source, instance.thumbnail]:
        if file and os.path.isfile(file.path):
            os.remove(file.path)

    hls_dir = os.path.join(settings.MEDIA_ROOT, "videos", str(instance.id))
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)