from django.urls import path
from rest_framework.routers import DefaultRouter
from geocoder.views import LocationSearchView, reverse_geocoder, geocoder, reverse_type_geocoder
from geocoder.viewsets import OpenNamesViewSet


urlpatterns = [
    path('search/', LocationSearchView.as_view()),
    path('reversegeocoder/<str:lon>/<str:lat>', reverse_geocoder, name='reverse_geocoder'),
    path('reversegeocoder/<str:type>/<str:lon>/<str:lat>', reverse_type_geocoder, name='reverse_type_geocoder'),
    path('geocoder/<str:search_term>', geocoder, name='geocoder')
]

router = DefaultRouter()
router.register(r'', OpenNamesViewSet, basename='opennames')
urlpatterns += router.urls
