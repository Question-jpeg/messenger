# Generated by Django 4.0.4 on 2022-05-13 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_user_managers_remove_user_username_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
