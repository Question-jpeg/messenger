# Generated by Django 4.0.3 on 2022-04-11 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(default='admin', max_length=255),
            preserve_default=False,
        ),
    ]
