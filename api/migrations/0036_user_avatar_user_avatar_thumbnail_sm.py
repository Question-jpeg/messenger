# Generated by Django 4.0.4 on 2022-05-24 08:23

import api.validators
from django.db import migrations, models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_alter_sentonmessage_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='api/avatars', validators=[api.validators.validate_file_size]),
        ),
        migrations.AddField(
            model_name='user',
            name='avatar_thumbnail_sm',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='api/avatars/thumbnails/small'),
        ),
    ]
