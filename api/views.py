from django.shortcuts import get_object_or_404, render
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ListingFilter
from api.permissions import IsObjInListingOwnerOrReadOnly, IsOwnerOrReadOnly

from api.serializers import CreateListingSerializer, ListingImageSerializer, ListingLocationSerializer, ListingSerializer
from .models import Listing, ListingImage, ListingLocation


class ListingViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    queryset = Listing.objects.prefetch_related('images').all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ListingFilter
    
    def get_serializer_context(self):
        return {'request': self.request, 'user_id': self.request.user.id, 'listing_id': self.kwargs.get('pk', None)}
    
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return CreateListingSerializer

        return ListingSerializer



class ListingImageViewSet(ModelViewSet):
    serializer_class = ListingImageSerializer
    permission_classes = [IsObjInListingOwnerOrReadOnly, IsAuthenticated]

    def get_serializer_context(self):
        return { 'request': self.request, 'listing_id': self.kwargs['listing_pk'] }

    def get_queryset(self):
        return ListingImage.objects.filter(listing_id=self.kwargs['listing_pk'])


class ListingLocationView(APIView):
    serializer_class = ListingLocationSerializer
    permission_classes = [IsObjInListingOwnerOrReadOnly, IsAuthenticated]

    def post(self, request, listing_pk):
        serializer = ListingLocationSerializer(data=request.data, context={'listing_id': listing_pk})
        serializer.is_valid(raise_exception=True)
        location = serializer.save()
        return Response(ListingLocationSerializer(location).data, status=status.HTTP_201_CREATED)

    def get(self, request, listing_pk):
        listing = get_object_or_404(Listing.objects.all(), pk=listing_pk)
        location = get_object_or_404(ListingLocation.objects.all(), listing=listing)
        return Response(ListingLocationSerializer(location).data, status=status.HTTP_200_OK)

    def delete(self, request, listing_pk):
        with transaction.atomic():
            listing = get_object_or_404(Listing.objects.all(), pk=listing_pk)
            location = get_object_or_404(ListingLocation.objects.all(), listing=listing)
            listing.location = None
            listing.save(update_fields=['location'])
            location.delete()
            
            return Response({}, status=status.HTTP_204_NO_CONTENT)


# class ListingImageView(APIView):
#     def get(self, request, image_id)