import operator
from django.db.models import Q, F, CharField
from django.db.models.functions import Greatest, Least, Cast, Concat
from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from api import serializers
from api.filters import ListingFilter
from api.pagination import DefaultPagination, MessagePagination
from api.permissions import IsUserOrReadOnly, IsObjInListingOwnerOrReadOnly, IsOwnerOrReadOnly, IsMessageOwnerOrReadOnly

from api.serializers import CategorySerializer, ChatMessageSerializer, CreateListingSerializer, CreateMessageSerializer, DeleteForAllMessageSerializer, DeleteForMeMessageSerializer, ListingImageSerializer, ListingSerializer, CustomTokenObtainPairSerializer, MarkAsReadMessageSerializer, MessageSerializer, UpdateMessageSerializer, UserCreateSerializer, UserExpoTokenSerializer, UserSerializer
from .models import Category, Listing, ListingImage, Message, User


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsUserOrReadOnly, IsAuthenticated]
    http_method_names = ['get', 'post', 'put']

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        
        return UserSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class ListingViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    queryset = Listing.objects.prefetch_related(
        'images').select_related('user').order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ListingFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description', 'user__name']
    ordering_fields = ['price', 'created_at']

    def get_serializer_context(self):
        return {'request': self.request, 'user_id': self.request.user.id, 'listing_id': self.kwargs.get('pk', None)}

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ListingSerializer
        return CreateListingSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        recent_listings = Listing.objects.prefetch_related('images').filter(
            user=request.user).order_by('-created_at')

        recent_listings = self.filter_queryset(recent_listings)

        page = self.paginate_queryset(recent_listings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_listings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListingImageViewSet(ModelViewSet):
    serializer_class = ListingImageSerializer
    permission_classes = [IsObjInListingOwnerOrReadOnly, IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request, 'listing_id': self.kwargs['listing_pk']}

    def get_queryset(self):
        return ListingImage.objects.filter(listing_id=self.kwargs['listing_pk'])


def prefRelMessages(user_id):
    resultquery = ((Q(from_user__id=user_id) & Q(is_deleted_for_from_user=False)) | (
            Q(to_user__id=user_id) & Q(is_deleted_for_to_user=False)))

    queryset = Message.objects.filter(resultquery)
    prefetch_fields = ['files', 'from_user', 'to_user', 'attached_listing__images',
                       'used_for_reply_message__files', 'used_for_reply_message__from_user', 'used_for_reply_message__attached_listing__images']
    select_fields = ['from_user', 'to_user', 'used_for_reply_message__from_user']
    base_lookup = "attached_messages__message"
    previous = ""


    queryset = queryset.select_related(*select_fields)
    for attached in range(100):
        prefetch_lookups = [
            previous + prefetch_field for prefetch_field in prefetch_fields]

        queryset = queryset.prefetch_related(*prefetch_lookups)

        previous += base_lookup + "__"

    return queryset


class MessageViewSet(ModelViewSet):
    permission_classes = [IsMessageOwnerOrReadOnly, IsAuthenticated]
    pagination_class = MessagePagination
    filter_backends = [SearchFilter]
    search_fields = ['text', 'from_user__name', 'to_user__name', 'used_for_reply_message__text',
                     'used_for_reply_message__from_user__name',
                     'attached_listing__title', 'attached_listing__description', 'attached_listing__user__name']
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        return prefRelMessages(self.request.user.id).order_by('-sent_at')

    def get_serializer_context(self):
        return {"from_user": self.request.user, "request": self.request}

    def get_serializer_class(self):
        if self.action == 'markRead':
            return MarkAsReadMessageSerializer
        if self.action == 'deleteForMe':
            return DeleteForMeMessageSerializer
        if self.action == 'deleteForAll':
            return DeleteForAllMessageSerializer
        if self.action == 'chatsView':
            return ChatMessageSerializer
        if self.request.method in permissions.SAFE_METHODS:
            return MessageSerializer
        if self.request.method == 'PUT':
            return UpdateMessageSerializer
        return CreateMessageSerializer

    @action(detail=False, methods=['put'])
    def markRead(self, request):
        serializer = MarkAsReadMessageSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put'])
    def deleteForMe(self, request):
        serializer = DeleteForMeMessageSerializer(
            data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put'])
    def deleteForAll(self, request):
        serializer = DeleteForAllMessageSerializer(
            data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def chatView(self, request):
        ids = request.GET.get('user__in', None)
        if ids:
            queryset = self.get_queryset().filter(Q(from_user__id__in=ids) | Q(to_user__id__in=ids))
            queryset = self.filter_queryset(queryset)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def chatsView(self, request):
        queryset = self.get_queryset().annotate(slug=Concat(Cast(Least('from_user', 'to_user'),
                                                                 output_field=CharField()), Cast(Greatest('from_user', 'to_user'), output_field=CharField()))).order_by('slug', '-sent_at').distinct('slug')
        self.search_fields = ['from_user__name', 'to_user__name']
        queryset = self.filter_queryset(queryset)

        queryset = sorted(queryset, key=operator.attrgetter(
            'sent_at'), reverse=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExpoPushTokenView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserExpoTokenSerializer

    def get(self, request):
        instance = get_object_or_404(User.objects.all(), id=request.user.id)
        if instance.expoPushToken == None or instance.expoPushToken == '':
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        return Response({"expoPushToken": instance.expoPushToken}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserExpoTokenSerializer(data=request.data, context={
            "user_id": request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def webSocketTester(request):
    return render(request, 'api/webSocketTester.html')