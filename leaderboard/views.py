from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum, Q
from rest_framework import generics, permissions
from accounts.models import User
from .serializers import LeaderboardSerializer, LeaderboardUserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Subquery, OuterRef, F, Window
from django.db.models.functions import Rank, Coalesce
from .pagination import LeaderboardPagination


class BaseLeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LeaderboardPagination 
    
    def get_queryset(self):
        start_date = self.get_start_date()
        period_type = 'daily' if isinstance(self, DailyLeaderboardView) else 'weekly'
        
        return User.objects.annotate(
            total_obtained_marks=Coalesce(
                Sum(
                    'testhistory__obtained_marks',
                    filter=Q(testhistory__created_at__gte=start_date)
                ),
                0
            )
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=F('total_obtained_marks').desc()
            )
        ).annotate(
            previous_rank=Subquery(
                User.objects.filter(
                    id=OuterRef('id')
                ).annotate(
                    prev_marks=Sum(
                        'testhistory__obtained_marks',
                        filter=Q(testhistory__created_at__range=[
                            self.get_previous_period_start(),
                            start_date
                        ])
                    )
                ).annotate(
                    prev_rank=Window(
                        expression=Rank(),
                        order_by=F('prev_marks').desc()
                    )
                ).values('prev_rank')[:1]
            )
        ).order_by('-total_obtained_marks')

    def get_previous_period_start(self):
        if isinstance(self, DailyLeaderboardView):
            return self.get_start_date() - timedelta(days=1)
        return self.get_start_date() - timedelta(weeks=1)
    
class DailyLeaderboardView(BaseLeaderboardView):
    @swagger_auto_schema(
        operation_id='leaderboard_daily',
        operation_summary='Get daily leaderboard',
        operation_description='''Get top users based on total marks obtained today.
        \n**Time Zone:** Uses server timezone
        \n**Reset Time:** 00:00:00 daily''',
        responses={
            200: LeaderboardSerializer(many=True),
            401: 'Unauthorized',
        },
        security=[{'Bearer': []}],
        tags=['Leaderboard'],
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True
            ), 
            openapi.Parameter(
            name='page',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Page number'
        ),
        openapi.Parameter(
            name='page_size',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Number of results per page (max 100)'
        )
        ]
    )
    def get_start_date(self):
        return timezone.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

class WeeklyLeaderboardView(BaseLeaderboardView):
    @swagger_auto_schema(
        operation_id='leaderboard_weekly',
        operation_summary='Get weekly leaderboard',
        operation_description='''Get top users based on total marks obtained this week.
        \n**Week Start:** Monday
        \n**Time Zone:** Uses server timezone
        \n**Reset Time:** 00:00:00 on Monday''',
        responses={
            200: LeaderboardSerializer(many=True),
            401: 'Unauthorized',
        },
        security=[{'Bearer': []}],
        tags=['Leaderboard'],
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True
            )
        ]
    )
    def get_start_date(self):
        today = timezone.now().date()
        # For Monday-based week (0=Monday)
        start_of_week = today - timedelta(days=today.weekday())
        return timezone.make_aware(
            datetime.combine(start_of_week, datetime.min.time())
        )