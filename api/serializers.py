from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from .models import Category, Listing, ListingImage, Message, MessageFile, SentOnMessage, User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)

        token['name'] = user.name
        token['email'] = user.email
        # token['avatar'] = user.avatar.url
        # token['avatar_thumbnail_sm'] = user.avatar_thumbnail_sm.url

        return token


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'password',
                  'email', 'name']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['name', 'email', 'avatar', 'avatar_thumbnail_sm']


class UserExpoTokenSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['expoPushToken']

    def validate_expoPushToken(self, value):
        if value == None or value == '':
            raise serializers.ValidationError("Expo Push Token must be set.")

        return value

    def save(self, **kwargs):
        expoPushToken = self.validated_data['expoPushToken']

        instance = get_object_or_404(
            User.objects.all(), id=self.context['user_id'])
        instance.expoPushToken = expoPushToken
        instance.save()
        return instance

class UserAvatarSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['avatar']

    def save(self, **kwargs):
        user_id = self.context['user_id']
        avatar = self.validated_data['avatar']
        
        user = get_object_or_404(User.objects.all(), pk=user_id)
        user.avatar = avatar
        user.avatar_thumbnail_sm = avatar
        user.save()

        return user

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
                  'category', 'user', 'location', 'description', 'created_at']

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
        child=serializers.ImageField(), default=[], allow_empty=True, write_only=True)

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
            listToCreate = [ListingImage(
                image=image, thumbnail_card=image, thumbnail_detail=image, listing_id=self.instance.id) for image in images]
            ListingImage.objects.bulk_create(listToCreate)

            return self.instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageFile
        fields = ['id', 'file']


class MessageReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    from_user = UserSerializer()
    attached_listing = ListingSerializer()
    files = MessageFileSerializer(many=True)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    from_user = UserSerializer()
    to_user = UserSerializer()
    attached_listing = ListingSerializer()
    used_for_reply_message = MessageReplySerializer()
    files = MessageFileSerializer(many=True)

    def to_representation(self, instance):
        self.fields['attached_messages'] = SentOnMessageSerializer(many=True)

        return super(MessageSerializer, self).to_representation(instance)


class SentOnMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentOnMessage
        fields = ['message']

    message = MessageSerializer()


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ['from_user']

    attached_messages = serializers.ListField(
        child=serializers.IntegerField(), default=[], allow_empty=True, write_only=True)
    files = serializers.ListField(
        child=serializers.FileField(), default=[], allow_empty=True, write_only=True)

    def save(self, **kwargs):
        with transaction.atomic():
            from_user = self.context['from_user']
            files = self.validated_data['files']
            attached_messages = self.validated_data['attached_messages']
            del self.validated_data['files']
            del self.validated_data['attached_messages']

            self.instance = Message.objects.create(
                **self.validated_data, from_user=from_user)

            listToCreateFiles = [MessageFile(
                message=self.instance, file=file) for file in files]

            listToCreateSentOnMessages = [SentOnMessage(message_parent=self.instance, message=message)
                                          for message in Message.objects.filter(Q(from_user=from_user) | Q(to_user=from_user)).filter(id__in=attached_messages)]

            MessageFile.objects.bulk_create(listToCreateFiles)
            SentOnMessage.objects.bulk_create(listToCreateSentOnMessages)

            return self.instance


class UpdateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ['from_user', 'to_user']

    def save(self, **kwargs):
        del self.validated_data['is_edited']
        return super().save(**self.validated_data, is_edited=True)


class DeleteForMeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['messages']

    messages = serializers.ListField(child=serializers.IntegerField())

    def save(self, **kwargs):
        from_user = self.context['from_user']
        messages = self.validated_data['messages']
        Message.objects.filter(from_user=from_user, pk__in=messages).update(
            is_deleted_for_from_user=True)
        Message.objects.filter(to_user=from_user, pk__in=messages).update(
            is_deleted_for_to_user=True)


class DeleteForAllMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['messages']

    messages = serializers.ListField(child=serializers.IntegerField())

    def save(self, **kwargs):
        from_user = self.context['from_user']
        messages = self.validated_data['messages']
        Message.objects.filter(Q(from_user=from_user)).filter(
            pk__in=messages).update(is_deleted_for_from_user=True, is_deleted_for_to_user=True)


class ChatMessageSerializer(MessageSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    from_user = UserSerializer()
    to_user = UserSerializer()
    attached_listing = ListingSerializer()
    used_for_reply_message = MessageReplySerializer()
    files = MessageFileSerializer(many=True)
