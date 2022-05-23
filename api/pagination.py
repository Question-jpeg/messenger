from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    page_size = 30

class MessagePagination(PageNumberPagination):
    page_size = 100