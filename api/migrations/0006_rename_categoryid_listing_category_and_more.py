# Generated by Django 4.0.3 on 2022-04-11 07:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_user_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='categoryId',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='listing',
            old_name='userId',
            new_name='user',
        ),
    ]