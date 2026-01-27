"""
URL configurations for the video application API.
Defines routes for listing videos, serving HLS manifests, and serving HLS segments.
"""
from django.urls import path
from .views import VideoListView, VideoHLSManifestView, VideoHLSSegmentView

urlpatterns = [
    path("video/", VideoListView.as_view(), name="video-list"),
    path("video/<int:movie_id>/<str:resolution>/index.m3u8",
         VideoHLSManifestView.as_view(), name="video-hls-manifest"),
    path("video/<int:movie_id>/<str:resolution>/<str:segment>/",
         VideoHLSSegmentView.as_view(), name="video-hls-segment"),
]
