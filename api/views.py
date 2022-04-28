from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ListingFilter
from api.pagination import DefaultPagination
from api.permissions import IsObjInListingOwnerOrReadOnly, IsOwnerOrReadOnly

from api.serializers import CategorySerializer, CreateListingSerializer, ListingImageSerializer, ListingSerializer
from .models import Category, Listing, ListingImage

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


class ListingImageViewSet(ModelViewSet):
    serializer_class = ListingImageSerializer
    permission_classes = [IsObjInListingOwnerOrReadOnly, IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request, 'listing_id': self.kwargs['listing_pk']}

    def get_queryset(self):
        return ListingImage.objects.filter(listing_id=self.kwargs['listing_pk'])