from decimal import Decimal
from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from .models import Category, Listing, ListingImage


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password',
                  'email', 'name']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'name', 'email']


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'thumbnail_card', 'thumbnail_detail']
        read_only_fields = ['thumbnail_card', 'thumbnail_detail']

    def save(self, **kwargs):
        image = ListingImage.objects.create(
            **self.validated_data, listing_id=self.context['listing_id'])
        return image


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'images', 'price',
                  'category', 'user', 'location', 'description']
        read_only_fields = ['user']

    images = ListingImageSerializer(many=True)
    location = serializers.SerializerMethodField(
        method_name='get_location_obj')

    def get_location_obj(self, obj):
        return {"latitude": obj.latitude, "longitude": obj.longitude}


class CreateListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'images', 'price',
                  'category', 'latitude', 'longitude', 'description']

    images = serializers.ListField(
        child=ListingImageSerializer(), default=[], allow_empty=True, write_only=True)

    def save(self, **kwargs):
        with transaction.atomic():
            pk = self.context['listing_id']
            user_id = self.context['user_id']
            title = self.validated_data['title']
            price = self.validated_data['price']
            category = self.validated_data['category']
            description = self.validated_data['description']
            latitude = self.validated_data['latitude']
            longitude = self.validated_data['longitude']

            try:
                listing = Listing.objects.get(pk=pk)
                listing.title = title
                listing.price = price
                listing.category = category
                listing.description = description
                listing.latitude = latitude
                listing.longitude = longitude
                listing.save()

                self.instance = listing
            except Listing.DoesNotExist:
                self.instance = Listing.objects.create(
                    title=title, price=price, category=category, description=description, latitude=latitude, longitude=longitude, user_id=user_id)

            images = self.validated_data['images']
            listingImages = [ListingImage(image=image, listing_id=self.instance.id)
                             for image in images]

            ListingImage.objects.bulk_create(listingImages)

            return self.instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']
