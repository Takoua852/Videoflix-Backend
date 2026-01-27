from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from video_app.models import Video
from .serializers import VideoListSerializer
from rest_framework.response import Response
from auth_app.api.authentication import CookieJWTAuthentication
import os
from django.http import HttpResponse, FileResponse
from rest_framework import status
from django.conf import settings


class VideoListView(ListAPIView):

    """Lists all available videos to authenticated users"""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer
    queryset = Video.objects.all().order_by("-created_at")

    def get(self, request, *args, **kwargs):
        videos = self.get_queryset()
        serializer = self.get_serializer(
            videos, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoHLSManifestView(APIView):
    
    """Serves HLS manifests to authenticated users """

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        video = Video.objects.filter(id=movie_id).first()
        if not video:
            return HttpResponse("Video not found", status=404)

        manifest_path = os.path.join(
            settings.MEDIA_ROOT,
            'videos',
            str(video.id),
            resolution,
            'index.m3u8'
        )

        if not os.path.exists(manifest_path):
            return HttpResponse(
                'Manifest not found',
                status=status.HTTP_404_NOT_FOUND
            )

        if not os.path.exists(manifest_path):
            return HttpResponse("Manifest not found", status=404)

        return FileResponse(
            open(manifest_path, "rb"),
            content_type="application/vnd.apple.mpegurl"
        )


class VideoHLSSegmentView(APIView):

    """Serves HLS video segments to authenticated users"""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        video = Video.objects.filter(id=movie_id).first()
        if not video:
            return HttpResponse("Video not found", status=404)

        segment_path = os.path.join(
            settings.MEDIA_ROOT,
            "videos",
            str(video.id),
            resolution,
            segment
        )

        if not os.path.exists(segment_path):
            return HttpResponse("Segment not found", status=404)

        return FileResponse(
            open(segment_path, "rb"),
            content_type="video/MP2T"
        )
