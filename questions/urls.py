from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectsViewSet, StreamsViewSet, ChaptersViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

router = DefaultRouter()
router.register(r'subjects', SubjectsViewSet, basename='subjects')
router.register(r'streams', StreamsViewSet, basename='streams')
router.register(r'chapters', ChaptersViewSet, basename='chapters')

urlpatterns = [
    path('', include(router.urls)),
]
