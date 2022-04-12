from django_filters.rest_framework import FilterSet
from .models import Listing


class ListingFilter(FilterSet):
    class Meta:
        model = Listing
        fields = {
            'category': ['exact']
        }
