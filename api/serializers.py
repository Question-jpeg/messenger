from django.db import transaction
from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from .models import Listing, ListingImage, ListingLocation


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password',
                  'email', 'name']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'name', 'email']


class ListingLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingLocation
        fields = ['latitude', 'longitude']

    def save(self, **kwargs):
        with transaction.atomic():
            listing = Listing.objects.get(pk=self.context['listing_id'])
            latitude = self.validated_data['latitude']
            longitude = self.validated_data['longitude']
            try:
                location = ListingLocation.objects.get(listing=listing)
                location.latitude = latitude
                location.longitude = longitude
                location.save(update_fields=['latitude', 'longitude'])

                self.instance = location
            except ListingLocation.DoesNotExist:
                self.instance = ListingLocation.objects.create(**self.validated_data, listing=listing)
            
            listing.location = self.instance
            listing.save(update_fields=['location'])

            return self.instance


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image_url']

    image_url = serializers.SerializerMethodField('get_image_url')

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url)

    def save(self, **kwargs):
        image = ListingImage.objects.create(**self.validated_data, listing_id=self.context['listing_id'])
        return image


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'images', 'price',
                  'category', 'user', 'location']

    images = ListingImageSerializer(many=True)
    location = ListingLocationSerializer()


class CreateListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['title', 'price', 'category']

    def save(self, **kwargs):
        pk = self.context['listing_id']
        user_id = self.context['user_id']
        title = self.validated_data['title']
        price = self.validated_data['price']
        category = self.validated_data['category']
        
        try:
            listing = Listing.objects.get(pk=pk)
            listing.title = title
            listing.price = price
            listing.category = category
            listing.save(update_fields=['title', 'price', 'category'])

            self.instance = listing
        except Listing.DoesNotExist:
            self.instance = Listing.objects.create(
                **self.validated_data, user_id=user_id)

            return self.instance
        
        

