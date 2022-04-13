from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('listings', views.ListingViewSet, basename='listings')

listings_router = routers.NestedDefaultRouter(router, 'listings', lookup='listing')
listings_router.register('images', views.ListingImageViewSet, basename='listing-images')

urlpatterns = [
    path('listings/<int:listing_pk>/location/', views.ListingLocationView.as_view()),
    path('media/images/<int:pk>/', views.getImage)
] + router.urls + listings_router.urls
