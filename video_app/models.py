from django.db import models


class VideoCategory(models.TextChoices):
    """Enumeration of possible video categories."""

    DRAMA = "Drama", "Drama"
    ROMANCE = "Romance", "Romance"
    ACTION = "Action", "Action"
    COMEDY = "Comedy", "Comedy"
    HORROR = "Horror", "Horror"
    DOCUMENTARY = "Documentary", "Documentary"
    OTHER = "Other", "Other"


class Video(models.Model):
    """Model representing a video uploaded by a user."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    source = models.FileField(
        upload_to="videos/source/",
        null=True,
        blank=True
    )

    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
        null=True
    )
    category = models.CharField(
        max_length=50,
        choices=VideoCategory.choices,
        default=VideoCategory.OTHER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def thumbnail_url(self):

        if self.thumbnail:
            return self.thumbnail.url
        return None
