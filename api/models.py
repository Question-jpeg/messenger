from django.db import models
from . import signals
from django.core.validators import MinValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from api.validators import validate_file_size


class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)    


class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title


class Listing(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='listings')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    description = models.TextField(null=True, blank=True)


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='api/images',
                              validators=[validate_file_size])
    thumbnail_card = ProcessedImageField(upload_to='api/images/thumbnails/small', format='JPEG', processors=[
                                         ResizeToFill(800, 400)], null=True, blank=True)
    thumbnail_detail = ProcessedImageField(
        upload_to='api/images/thumbnails/large', format='JPEG', processors=[ResizeToFill(900, 900)], null=True, blank=True)

    def save(self, *args, **kwargs):
        self.thumbnail_card = self.image.file
        self.thumbnail_detail = self.image.file
        super(ListingImage, self).save(*args, **kwargs)
