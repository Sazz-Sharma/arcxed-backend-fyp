from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectsViewSet, StreamsViewSet, ChaptersViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Question API",
        default_version='v1',
        description="API documentation for Subjects, Streams, and Chapters",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],  # Change to [IsAdminUser] if needed
)

router = DefaultRouter()
router.register(r'subjects', SubjectsViewSet, basename='subjects')
router.register(r'streams', StreamsViewSet, basename='streams')
router.register(r'chapters', ChaptersViewSet, basename='chapters')

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
