from django.contrib import admin
from video_app.models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):

    list_display = ("title", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "description")
