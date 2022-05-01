# Generated by Django 4.0.4 on 2022-04-28 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_rename_thumbnail_sm_listingimage_thumbnail_card_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='location',
        ),
        migrations.AddField(
            model_name='listing',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.DeleteModel(
            name='ListingLocation',
        ),
    ]