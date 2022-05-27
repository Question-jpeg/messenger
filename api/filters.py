from django_filters.rest_framework import FilterSet
from .models import Listing, Message


class ListingFilter(FilterSet):
    class Meta:
        model = Listing
        fields = {
            'category': ['exact'],
            'user': ['exact']
        }

# class MessageFilter(django_filters.FilterSet):
#     class Meta:
#         model = Message
#         fields = {
#             'user__in': ['exact']
#         }