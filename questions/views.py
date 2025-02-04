from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Subjects, Streams, Chapters
from .serializers import SubjectsSerializer, StreamsSerializer, ChaptersSerializer
from .permissions import IsSuperUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SubjectsViewSet(viewsets.ModelViewSet):
    queryset = Subjects.objects.all()
    serializer_class = SubjectsSerializer
    permission_classes = [IsSuperUser]

    @swagger_auto_schema(
        operation_description="Retrieve a list of subjects",
        responses={200: SubjectsSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class StreamsViewSet(viewsets.ModelViewSet):
    queryset = Streams.objects.all()
    serializer_class = StreamsSerializer
    permission_classes = [IsSuperUser]

    @swagger_auto_schema(
        operation_description="Retrieve a list of streams",
        responses={200: StreamsSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ChaptersViewSet(viewsets.ModelViewSet):
    queryset = Chapters.objects.all()
    serializer_class = ChaptersSerializer
    permission_classes = [IsSuperUser]

    @swagger_auto_schema(
        operation_description="Retrieve a list of chapters",
        responses={200: ChaptersSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)