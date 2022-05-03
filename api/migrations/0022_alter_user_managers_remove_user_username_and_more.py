# Generated by Django 4.0.4 on 2022-05-03 09:31

import api.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_remove_listing_location_listing_latitude_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', api.managers.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
