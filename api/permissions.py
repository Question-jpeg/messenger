from rest_framework import permissions
from api.models import Listing

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user

class IsUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj == request.user

class IsObjInListingOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (Listing.objects.get(pk=view.kwargs['listing_pk'])).user == request.user

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.listing.user == request.user

class IsMessageOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.to_user.id == request.user.id:
            if (request.method in permissions.SAFE_METHODS):
                return True
            return False

        return obj.from_user.id == request.user.id

class IsMessageReceiverOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.to_user.id == request.user.id or obj.from_user.id == request.user.id