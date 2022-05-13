from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ListingFilter
from api.pagination import DefaultPagination
from api.permissions import IsObjInListingOwnerOrReadOnly, IsOwnerOrReadOnly

from api.serializers import CategorySerializer, CreateListingSerializer, ListingImageSerializer, ListingSerializer, CustomTokenObtainPairSerializer
from .models import Category, Listing, ListingImage

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