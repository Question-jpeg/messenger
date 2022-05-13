from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ListingFilter
from api.pagination import DefaultPagination
from api.permissions import IsObjInListingOwnerOrReadOnly, IsOwnerOrReadOnly

from api.serializers import CategorySerializer, CreateListingSerializer, ListingImageSerializer, ListingSerializer, CustomTokenObtainPairSerializer, UserExpoTokenSerializer, UserSerializer
from .models import Category, Listing, ListingImage, User

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAdminUser()]

class ListingViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    queryset = Listing.objects.prefetch_related('images').all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ListingFilter
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        return {'request': self.request, 'user_id': self.request.user.id, 'listing_id': self.kwargs.get('pk', None)}

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ListingSerializer
        return CreateListingSerializer

    @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def my(self, request):
        recent_listings = Listing.objects.all().filter(user=request.user).order_by('-created_at')

        for backend in self.filter_backends:
            recent_listings = backend().filter_queryset(self.request, recent_listings, view=self)
    
        page = self.paginate_queryset(recent_listings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_listings, many=True)
        return Response(serializer.data)


class ListingImageViewSet(ModelViewSet):
    serializer_class = ListingImageSerializer
    permission_classes = [IsObjInListingOwnerOrReadOnly, IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request, 'listing_id': self.kwargs['listing_pk']}

    def get_queryset(self):
        return ListingImage.objects.filter(listing_id=self.kwargs['listing_pk'])

class expoPushToken(APIView):
    permission_classes  = [IsAuthenticated]
    serializer_class = UserExpoTokenSerializer

    def get(self, request):
        instance = get_object_or_404(User.objects.all(), id=request.user.id)
        if instance.expoPushToken == None or instance.expoPushToken == '':
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({ "expoPushToken": instance.expoPushToken }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserExpoTokenSerializer(data=request.data, context={ "user_id": request.user.id })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
