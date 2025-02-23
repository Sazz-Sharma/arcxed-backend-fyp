from django.shortcuts import render

from rest_framework import viewsets, status
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

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

@swagger_auto_schema(
    method='post',
    request_body=CustomTestSerializer,
    responses={
        200: openapi.Response(
            description="Custom test generated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'test_details': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'total_marks': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'time_minutes': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'subjects_covered': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_INTEGER)
                            )
                        }
                    ),
                    'questions': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    )
                }
            )
        ),
        400: "Invalid input data",
        404: "Subject or chapter not found"
    },
    operation_description="Generate a custom test based on user-selected subjects, chapters, and number of questions.",
    operation_summary="Create Custom Test"
)
@api_view(['POST'])
def create_custom_test(request):
    '''
    Payload:
                {
            "subjects": [
                {
                "subject_id": 1,
                "chapters": [
                    {
                    "chapter_id": 1,
                    "num_questions": 5
                    }
                ]
                }
            ],
            "time_minutes": 30
            }
    '''
    serializer = CustomTestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    selected_questions = []
    total_marks = 0
    stream = get_object_or_404(Streams, stream_name='IOE')  # Or make this configurable

    for subject_data in data['subjects']:
        subject = get_object_or_404(Subjects, id=subject_data['subject_id'])
        
        for chapter_data in subject_data['chapters']:
            chapter = get_object_or_404(Chapters, id=chapter_data['chapter_id'], sub_id=subject)
            topics = Topics.objects.filter(chapter=chapter)
            
            # Get random questions
            questions = HeroQuestions.objects.filter(
                topic__in=topics,
                stream=stream
            ).order_by('?')[:chapter_data['num_questions']]
            
            if len(questions) < chapter_data['num_questions']:
                return Response({
                    'error': f'Not enough questions for {subject.subject_name} - {chapter.chapter_name}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            selected_questions.extend(questions)
            total_marks += sum(q.marks for q in questions)

    serializer = HeroQuestionsWithoutAnswerSerializer(selected_questions, many=True)
    
    return Response({
        'test_details': {
            'total_questions': len(selected_questions),
            'total_marks': total_marks,
            'time_minutes': data['time_minutes'],
            'subjects_covered': [s['subject_id'] for s in data['subjects']]
        },
        'questions': serializer.data
    })
    
    

from django.db.models import Q

@swagger_auto_schema(
    method='post',
    request_body=TestResultSerializer,
    responses={
        200: "Test results calculated successfully",
        400: "Invalid input data"
    },
    operation_description="Check test results and calculate scores",
    operation_summary="Check Test Results"
)
@api_view(['POST'])
def check_test_result(request):
    serializer = TestResultSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Get all question IDs from the request
    question_ids = [ans['question_id'] for ans in serializer.validated_data['answers']]
    
    # Fetch all relevant questions with answers
    questions = HeroQuestions.objects.filter(
        Q(question__id__in=question_ids)).select_related('question').only('id', 'marks', 'question__answer')
    
    
    # Create a mapping of question ID to correct answer and marks
    correct_answers = {
        q.question.id: {
            'correct_answer': q.question.answer,
            'marks': q.marks
        } for q in questions
    }
    
    # Calculate results
    total_score = 0
    results = []
    
    for answer in serializer.validated_data['answers']:
        q_id = answer['question_id']
        user_answer = answer['user_answer']
        
        if q_id not in correct_answers:
            results.append({
                'question_id': q_id,
                'error': 'Question not found',
                'is_correct': False,
                'marks_obtained': 0
            })
            continue
            
        correct = correct_answers[q_id]
        is_correct = user_answer.strip().lower() == correct['correct_answer'].strip().lower()
        
        if is_correct:
            total_score += correct['marks']
        
        results.append({
            'question_id': q_id,
            'user_answer': user_answer,
            'correct_answer': correct['correct_answer'],
            'is_correct': is_correct,
            'marks_obtained': correct['marks'] if is_correct else 0
        })
    
    return Response({
        'total_score': total_score,
        'total_questions': len(results),
        'correct_answers': sum(1 for r in results if r['is_correct']),
        'detailed_results': results
    })