from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('listings', views.ListingViewSet, basename='listings')
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('messages', views.MessageViewSet, basename='messages')

listings_router = routers.NestedDefaultRouter(router, 'listings', lookup='listing')
listings_router.register('images', views.ListingImageViewSet, basename='listing-images')

urlpatterns = [
    path('expoPushToken/', views.ExpoPushTokenView.as_view()),
] + router.urls + listings_router.urls
