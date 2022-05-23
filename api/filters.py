from django_filters.rest_framework import FilterSet
from .models import Listing, Message


class ListingFilter(FilterSet):
    class Meta:
        model = Listing
        fields = {
            'category': ['exact']
        }

class MessageFilter(FilterSet):
    class Meta:
        model = Message
        fields = {
            'from_user__id': ['range'],
            'to_user__id': ['range']
        }