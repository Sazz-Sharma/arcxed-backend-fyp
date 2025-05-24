from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

router = DefaultRouter()
router.register(r'subjects', SubjectsViewSet, basename='subjects')
router.register(r'streams', StreamsViewSet, basename='streams')
router.register(r'chapters', ChaptersViewSet, basename='chapters')
router.register(r'topics', TopicsViewSet, basename='topics')

router.register(r'questions-base', QuestionViewSet, basename='question-base')
# router.register(r'hero-questions', HeroQuestionViewSet, basename='hero-question')
router.register(r'combined-hero-questions', CombinedHeroQuestionViewSet, basename='combinedheroquestion')


urlpatterns = [
    path('', include(router.urls)),
    path('ioe/mocktest/', generate_mock_test, name='mock-test'), 
    path('ioe/custom-test/', create_custom_test, name='custom-test'), 
    path('tests/generated/<int:test_paper_id>/submit/', TestSubmissionView.as_view(), name='test-submit'),


     path('history/', TestHistoryListView.as_view(), name='test-history-list'),
    path('history/<int:id>/', TestHistoryDetailView.as_view(), name='test-history-detail'), # Use 'id' to match lookup_field
    path('stats/overall/', OverallStatsView.as_view(), name='overall-stats'),
    path('stats/by-subject/', SubjectPerformanceStatsView.as_view(), name='subject-stats'),
    path('stats/by-chapter/', ChapterPerformanceStatsView.as_view(), name='chapter-stats'),
    path('stats/by-topic/', TopicPerformanceStatsView.as_view(), name='topic-stats'),

]

