from django.shortcuts import render

from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

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
    
    

@api_view(['GET'])
def generate_mock_test(request):
    syllabus_data = [
        {"Subject": "English",
"Total_marks": 22,
"Number_of_questions": 18,
"Chapters":{
    "Reading Passage":{"mark1":0, "mark2":4},
    "Grammar":{"mark1":10, "mark2":0},
    "Vocabulary":{"mark1":2, "mark2":0},
    "Phonemes and Stress":{"mark1":2, "mark2":0}
    }
},
{
    "Subject": "Maths",
    "Total_marks": 50,
    "Number_of_questions": 25, 
    "Chapters":{
        "Set and Function":{"mark1":1, "mark2":1},
        "Algebra":{"mark1":2, "mark2":4},
        "Trigonometry":{"mark1":1, "mark2":2},
        "Coordinate Geometry":{"mark1":2, "mark2":4},
        "Calculus":{"mark1":3, "mark2":4},
        "Vectors": {"mark1":1, "mark2":1}
    }
},
{
    "Subject": "Physics",
    "Total_marks": 40,
    "Number_of_questions": 25,
    "Chapters":{
        "Mechanics":{"mark1":2, "mark2":4},
        "Heat and Thermodynamics":{"mark1":2, "mark2":1},
        "Wave and Optics":{"mark1":2, "mark2":3},
        "Electricity and Magnetism":{"mark1":2, "mark2":4},
        "Modern Physics and Electronics":{"mark1":2, "mark2":3}
    }
},
{
    "Subject": "Chemistry",
    "Total_marks": 20,
    "Number_of_questions": 16,
    "Chapters":{
        "Physical Chemistry":{"mark1":6, "mark2":3},
        "Inorganic Chemistry":{"mark1":3, "mark2":1},
        "Organic Chemistry":{"mark1":3, "mark2":0}
    }
}
    ]
    
    try:
        stream = Streams.objects.get(stream_name='IOE')
    except Streams.DoesNotExist:
        return JsonResponse({'error': 'IOE stream not found'}, status=404)
    
    selected_questions = []
    
    for subject_info in syllabus_data:
        subject_name = subject_info['Subject']
        try:
            subject = Subjects.objects.get(subject_name=subject_name)
        except Subjects.DoesNotExist:
            continue
        
        chapters_info = subject_info['Chapters']
        for chapter_name, marks_info in chapters_info.items():
            try:
                chapter = Chapters.objects.get(sub_id=subject, chapter_name=chapter_name)
            except Chapters.DoesNotExist:
                continue
            
            topics = Topics.objects.filter(chapter=chapter)
            
            # Fetch 1-mark questions
            num_mark1 = marks_info['mark1']
            if num_mark1 > 0:
                questions = HeroQuestions.objects.filter(
                    topic__in=topics,
                    marks=1,
                    stream=stream
                ).order_by('?')[:num_mark1]
                selected_questions.extend(questions)
            
            # Fetch 2-mark questions
            num_mark2 = marks_info['mark2']
            if num_mark2 > 0:
                questions = HeroQuestions.objects.filter(
                    topic__in=topics,
                    marks=2,
                    stream=stream
                ).order_by('?')[:num_mark2]
                selected_questions.extend(questions)
    
    serializer = HeroQuestionsWithoutAnswerSerializer(selected_questions, many=True)
    return Response(serializer.data)