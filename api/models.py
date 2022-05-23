from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from . import signals
from .managers import UserManager
from api.validators import validate_file_size


class User(AbstractUser):
    name = models.CharField(max_length=255)
    username = None
    email = models.EmailField(_('email address'), unique=True)

    expoPushToken = models.CharField(
        max_length=255, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


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
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='api/images',
                              validators=[validate_file_size])
    thumbnail_card = ProcessedImageField(upload_to='api/images/thumbnails/small', format='JPEG', processors=[
                                         ResizeToFill(800, 400)], null=True, blank=True)
    thumbnail_detail = ProcessedImageField(
        upload_to='api/images/thumbnails/large', format='JPEG', processors=[ResizeToFill(900, 900)], null=True, blank=True)



class Message(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    text = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    used_for_reply_message = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replied_messages', null=True, blank=True)
    attached_listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, related_name='replied_messages', null=True, blank=True)

    is_deleted_for_from_user = models.BooleanField(default=False)
    is_deleted_for_to_user = models.BooleanField(default=False)

    is_edited = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.text

class MessageFile(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="api/messageFiles", validators=[validate_file_size])


class SentOnMessage(models.Model):
    message_parent = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="attached_messages")
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="parent_messages")

    def __str__(self) -> str:
        return "Пересланное сообщение"
