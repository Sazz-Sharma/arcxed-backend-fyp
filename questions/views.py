from django.shortcuts import render

from rest_framework import viewsets, status, views, generics
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser, IsSuperUserOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db import transaction 
from django.db.models import Count, Sum, Avg, F, Case, When, IntegerField, FloatField
from django.db.models.functions import Cast
import json
from django.db import IntegrityError
from .filters import HeroQuestionFilter 
from django_filters.rest_framework import DjangoFilterBackend

class SubjectsViewSet(viewsets.ModelViewSet):
    queryset = Subjects.objects.all()
    serializer_class = SubjectsSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve a list of subjects",
        responses={200: SubjectsSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
class TopicsViewSet(viewsets.ModelViewSet):
    queryset = Topics.objects.all()
    serializer_class = TopicsSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve a list of topics",
        responses={200: SubjectsSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class StreamsViewSet(viewsets.ModelViewSet):
    queryset = Streams.objects.all()
    serializer_class = StreamsSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve a list of streams",
        responses={200: StreamsSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ChaptersViewSet(viewsets.ModelViewSet):
    queryset = Chapters.objects.all()
    serializer_class = ChaptersSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve a list of chapters",
        responses={200: ChaptersSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class QuestionViewSet(viewsets.ModelViewSet): # For managing base Questions
    """
    API endpoint for managing base Questions in the question bank.
    """
    queryset = Questions.objects.all().select_related('topic__chapter__sub_id').order_by('-id')
    serializer_class = QuestionsSerializer # Use your existing QuestionsSerializer
    # permission_classes = [IsSuperUserOrReadOnly] # Apply permissions as needed

    # View-specific filtering (if you want it, otherwise remove filter_backends and filterset_fields)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'topic__id': ['exact'],
        'topic__chapter__id': ['exact'],
        'topic__chapter__sub_id__id': ['exact'], # subject id
        'question': ['icontains']
    }
    # No default pagination is applied here unless you explicitly add it.

    @swagger_auto_schema(
        operation_summary="List all base questions",
        manual_parameters=[
            openapi.Parameter('topic__id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('topic__chapter__id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('topic__chapter__sub_id__id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('question__icontains', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Create a new base question", request_body=QuestionsSerializer)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Retrieve a base question")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update a base question", request_body=QuestionsSerializer)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Partially update a base question", request_body=QuestionsSerializer)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete a base question")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# class HeroQuestionViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for managing Hero Questions (questions for tests).
#     Supports CRUD and filtering by subject, chapter, topic, stream, marks, and base question ID.
#     """
#     queryset = HeroQuestions.objects.select_related(
#         'question__topic', 'topic__chapter__sub_id', 'stream' # Optimize queries
#     ).all().order_by('-id')
#     # permission_classes = [IsSuperUserOrReadOnly] # Apply permissions as needed

#     # --- View-specific filtering and pagination ---
#     # This ensures only this ViewSet uses these settings.
#     filter_backends = [DjangoFilterBackend] # Enable django-filter
#     filterset_class = HeroQuestionFilter    # Use the custom filter

#     # If you want pagination ONLY for this endpoint:
#     # from rest_framework.pagination import PageNumberPagination
#     # class StandardResultsSetPagination(PageNumberPagination):
#     #     page_size = 10
#     #     page_size_query_param = 'page_size'
#     #     max_page_size = 100
#     # pagination_class = StandardResultsSetPagination # Uncomment to enable pagination for this viewset

#     def get_serializer_class(self):
#         if self.action in ['create', 'update', 'partial_update']:
#             return HeroQuestionCreateUpdateSerializer
#         # Use your existing HeroQuestionsSerializer for list/retrieve
#         return HeroQuestionsSerializer

#     @swagger_auto_schema(
#         operation_summary="List Hero Questions",
#         responses={200: HeroQuestionsSerializer(many=True)}
#         # drf-yasg will automatically pick up parameters from filterset_class
#     )
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)

#     @swagger_auto_schema(
#         operation_summary="Create a new Hero Question",
#         request_body=HeroQuestionCreateUpdateSerializer,
#         responses={
#             201: HeroQuestionsSerializer(), # Show using the read serializer
#             400: "Validation Error"
#         }
#     )
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         instance = serializer.save()
#         # Return the representation using your existing HeroQuestionsSerializer for reads
#         read_serializer = HeroQuestionsSerializer(instance, context={'request': request})
#         headers = self.get_success_headers(read_serializer.data)
#         return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#     @swagger_auto_schema(
#         operation_summary="Retrieve a specific Hero Question",
#         responses={200: HeroQuestionsSerializer(), 404: "Not Found"}
#     )
#     def retrieve(self, request, *args, **kwargs):
#         return super().retrieve(request, *args, **kwargs)

#     @swagger_auto_schema(
#         operation_summary="Update a Hero Question",
#         request_body=HeroQuestionCreateUpdateSerializer,
#         responses={200: HeroQuestionsSerializer(), 400: "Validation Error", 404: "Not Found"}
#     )
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         updated_instance = serializer.save()
#         read_serializer = HeroQuestionsSerializer(updated_instance, context={'request': request})
#         return Response(read_serializer.data)

#     @swagger_auto_schema(
#         operation_summary="Partially update a Hero Question",
#         request_body=HeroQuestionCreateUpdateSerializer,
#         responses={200: HeroQuestionsSerializer(), 400: "Validation Error", 404: "Not Found"}
#     )
#     def partial_update(self, request, *args, **kwargs):
#         kwargs['partial'] = True # Ensure partial update logic is triggered
#         return self.update(request, *args, **kwargs) # Reuse the update method

#     @swagger_auto_schema(
#         operation_summary="Delete a Hero Question",
#         responses={204: "No Content", 404: "Not Found"}
#     )
#     def destroy(self, request, *args, **kwargs):
#         return super().destroy(request, *args, **kwargs)
    

class CombinedHeroQuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Hero Questions along with their base Question data.

    - POST: Creates a Hero Question and its underlying base Question in one request.
    - GET: Retrieves Hero Questions with full details, including nested Question,
           Topic (for HeroQuestion), and Stream objects.
    - PUT/PATCH: Updates a Hero Question and/or its underlying base Question.
    - DELETE: Deletes a Hero Question (and its base Question if CASCADE is set).

    The representation of related Topic and Stream objects in API responses
    (e.g., in GET requests or after a POST/PUT) will use your existing
    TopicsSerializer and StreamsSerializer.
    """

    # Optimized queryset:
    # Fetches related objects in a more efficient way to reduce DB queries.
    # This assumes HeroQuestions.topic and Questions.topic are FKs to Topics,
    # and Topics.chapter is an FK to Chapters.
    queryset = HeroQuestions.objects.select_related(
        'topic',                    # HeroQuestions.topic (ForeignKey to Topics)
        'topic__chapter',           # HeroQuestions.topic.chapter (if Topics.chapter is FK to Chapters)
        'stream',                   # HeroQuestions.stream (ForeignKey to Streams)
        'question',                 # HeroQuestions.question (ForeignKey to Questions)
        'question__topic',          # HeroQuestions.question.topic (Questions.topic, FK to Topics)
        'question__topic__chapter'  # HeroQuestions.question.topic.chapter
    ).all()

    def get_serializer_class(self):
        """
        Dynamically selects the serializer class based on the action.
        - For 'list' and 'retrieve' (read actions): HeroQuestionsReadOnlySerializer.
        - For 'create', 'update', 'partial_update' (write actions): CombinedHeroQuestionCreateUpdateSerializer.
        """
        if self.action in ['list', 'retrieve']:
            return HeroQuestionsReadOnlySerializer
        # For 'create', 'update', 'partial_update'
        return CombinedHeroQuestionCreateUpdateSerializer

    @swagger_auto_schema(
        operation_summary="List all Combined Hero Questions",
        operation_description=(
            "Retrieves a list of all Hero Questions. "
            "Each item includes the HeroQuestion's own topic and stream, "
            "and the nested base Question with its own topic. "
            "Representations of 'topic' and 'stream' objects use your existing serializers."
        ),
        responses={200: HeroQuestionsReadOnlySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Combined Hero Question",
        operation_description=(
            "Retrieves a specific Hero Question by its ID. "
            "Includes the HeroQuestion's own topic and stream, "
            "and the nested base Question with its own topic. "
            "Representations of 'topic' and 'stream' objects use your existing serializers."
        ),
        responses={200: HeroQuestionsReadOnlySerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new Combined Hero Question",
        operation_description=(
            "Creates a new Hero Question and its underlying base Question simultaneously. "
            "You need to provide:\n"
            "- For the base Question: `question_text`, `question_options` (JSON), `question_answer` (JSON), "
            "and optionally `question_base_topic_id` (ID of the Topic for the base Question).\n"
            "- For the HeroQuestion: `hero_topic_id` (ID of the Topic for the HeroQuestion context), "
            "`stream_id` (ID of the Stream), and `marks`.\n"
            "The response will be the newly created HeroQuestion, with nested objects formatted "
            "using your existing Topic/Stream serializers via HeroQuestionsReadOnlySerializer."
        ),
        request_body=CombinedHeroQuestionCreateUpdateSerializer,
        responses={
            201: HeroQuestionsReadOnlySerializer(), # Response uses read-only serializer
            400: "Validation Error: Check input data and required fields."
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) # Calls serializer.save() -> serializer.create()
        # serializer.data will use CombinedHeroQuestionCreateUpdateSerializer's to_representation,
        # which in turn uses HeroQuestionsReadOnlySerializer.
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        operation_summary="Update a Combined Hero Question (PUT)",
        operation_description=(
            "Updates an existing Hero Question and its underlying base Question. "
            "Requires all fields expected by `CombinedHeroQuestionCreateUpdateSerializer` for a full update.\n"
            "The response will show the updated object, with nested objects formatted "
            "using your existing Topic/Stream serializers via HeroQuestionsReadOnlySerializer."
        ),
        request_body=CombinedHeroQuestionCreateUpdateSerializer,
        responses={
            200: HeroQuestionsReadOnlySerializer(), # Response uses read-only serializer
            400: "Validation Error: Check input data and required fields."
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False) # For PUT, partial is False
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer) # Calls serializer.save() -> serializer.update()
        # serializer.data will use to_representation.
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Partially update a Combined Hero Question (PATCH)",
        operation_description=(
            "Partially updates an existing Hero Question and/or its underlying base Question. "
            "Provide only the fields you want to change.\n"
            "The response will show the updated object, with nested objects formatted "
            "using your existing Topic/Stream serializers via HeroQuestionsReadOnlySerializer."
        ),
        request_body=CombinedHeroQuestionCreateUpdateSerializer, # Input is still based on this
        responses={
            200: HeroQuestionsReadOnlySerializer(), # Response uses read-only serializer
            400: "Validation Error: Check input data."
        }
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs) # Reuses the update logic

    @swagger_auto_schema(
        operation_summary="Delete a Combined Hero Question",
        operation_description=(
            "Deletes a Hero Question by its ID. "
            "If `HeroQuestions.question` has `on_delete=models.CASCADE`, "
            "the associated base Question will also be deleted."
        ),
        responses={
            204: "No Content: Successfully deleted.",
            404: "Not Found: HeroQuestion with the given ID does not exist."
        }
    )
    def perform_destroy(self, instance):
        question_to_check = instance.question
        # Delete the HeroQuestion instance first
        super().perform_destroy(instance)

        # Now check if the Question is orphaned
        if question_to_check:
            if not question_to_check.hero_instances.exists():
                question_to_check.delete()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
    generated_test_paper = GeneratedTestPaper.objects.create(
        stream=stream,
        total_marks=sum(q.marks for q in selected_questions),
        total_questions=len(selected_questions),
        created_by=request.user, 
        test_type='mock', 
        subjects_included=[s.id for s in Subjects.objects.all()]
          )
    
    for question in selected_questions:
        TestQuestionLink.objects.create(
            test_id=generated_test_paper,
            question_id=question
        )
        
    # generated_test_paper.questions.set(selected_questions)

    question_serializer = HeroQuestionsWithoutAnswerSerializer(selected_questions, many=True)
    # return Response(serializer.data)
    
    test_paper_serializer = GeneratedTestPaperSerializer(generated_test_paper)
    
    return Response({
        'test_details': test_paper_serializer.data,
        'questions': question_serializer.data
    })



@swagger_auto_schema(
    method='post',
    request_body=CustomTestSerializer, # Input definition is fine
    responses={
        201: openapi.Response(
            description="Custom test generated and saved successfully.",
            # --- Simpler Schema Definition ---
            # Let drf-yasg infer from serializers if possible, or use basic types/refs.
            # Avoid accessing .fields manually here.
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    # Option A: Use basic types as placeholders (less descriptive but avoids the error)
                    'test_details': openapi.Schema(type=openapi.TYPE_OBJECT, description="Details of the created test paper"),
                    'questions': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        description="List of questions for the test (without answers)"
                    )

                }
             )
            # --- End Simpler Schema Definition ---
        ),
        400: "Invalid input data or not enough questions.",
        401: "Authentication credentials were not provided.",
        404: "Stream, Subject or Chapter not found."
    },
    operation_description=(
        "Generate a custom test based on user-selected subjects, chapters, and number of questions. "
        "The generated test paper and its associated questions are saved to the database."
    ),
    operation_summary="Create and Save Custom Test"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Ensure user is logged in to create a test
@transaction.atomic # Wrap database operations in a transaction
def create_custom_test(request):
    '''
    Payload Example:
                {
            "subjects": [
                {
                "subject_id": 1,
                "chapters": [
                    {
                    "chapter_id": 1,
                    "num_questions": 5
                    },
                    {
                    "chapter_id": 2,
                    "num_questions": 3
                    }
                ]
                },
                {
                "subject_id": 2,
                "chapters": [
                    {
                    "chapter_id": 5,
                    "num_questions": 10
                    }
                ]
                }
            ],
            "time_minutes": 30 # Note: time_minutes is in the input but not directly stored in GeneratedTestPaper model
            }
    '''
    serializer = CustomTestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    selected_questions = []
    total_marks = 0
    subject_ids_included = set() # Keep track of subjects actually used

    # --- Get Stream (Consider making this dynamic or configurable if needed) ---
    try:
        # Use filter+first for potentially better performance if multiple 'IOE' streams could exist
        stream = Streams.objects.get(stream_name='IOE')
    except Streams.DoesNotExist:
        return Response({'error': 'Stream "IOE" not found. Cannot create test.'}, status=status.HTTP_404_NOT_FOUND)

    # --- Question Selection Logic (Similar to before) ---
    for subject_data in data['subjects']:
        try:
            subject = Subjects.objects.get(id=subject_data['subject_id'])
        except Subjects.DoesNotExist:
             return Response({'error': f"Subject with ID {subject_data['subject_id']} not found."}, status=status.HTTP_404_NOT_FOUND)

        subject_has_questions = False # Flag to track if any questions were added for this subject
        for chapter_data in subject_data['chapters']:
            try:
                chapter = Chapters.objects.get(id=chapter_data['chapter_id'], sub_id=subject)
            except Chapters.DoesNotExist:
                return Response({'error': f"Chapter with ID {chapter_data['chapter_id']} not found for Subject {subject.subject_name}."}, status=status.HTTP_404_NOT_FOUND)

            # Ensure num_questions is positive
            num_questions_requested = chapter_data['num_questions']
            if num_questions_requested <= 0:
                continue # Skip chapters with zero or negative requested questions

            topics = Topics.objects.filter(chapter=chapter)
            if not topics.exists():
                 # Optionally warn or error if a selected chapter has no topics
                 # print(f"Warning: Chapter '{chapter.chapter_name}' has no topics.")
                 continue # Skip if chapter has no topics

            # Get random questions from HeroQuestions linked to topics in this chapter and the correct stream
            questions = HeroQuestions.objects.filter(
                topic__in=topics,
                stream=stream
            ).order_by('?')[:num_questions_requested]

            # Check if enough questions were found
            if len(questions) < num_questions_requested:
                return Response({
                    'error': f'Not enough questions available for {subject.subject_name} - {chapter.chapter_name}. Found {len(questions)}, requested {num_questions_requested}.'
                }, status=status.HTTP_400_BAD_REQUEST)

            selected_questions.extend(questions)
            total_marks += sum(q.marks for q in questions)
            subject_has_questions = True # Mark that we added questions for this subject

        # Add subject ID to the set if questions were actually selected from it
        if subject_has_questions:
             subject_ids_included.add(subject.id)


    # --- Check if any questions were selected overall ---
    if not selected_questions:
         return Response({'error': 'No questions could be selected based on the provided criteria or requested numbers.'}, status=status.HTTP_400_BAD_REQUEST)

    total_questions_count = len(selected_questions)

    # --- Create GeneratedTestPaper instance ---
    generated_test_paper = GeneratedTestPaper.objects.create(
        stream=stream,
        total_marks=total_marks,
        total_questions=total_questions_count,
        created_by=request.user,
        test_type='CUSTOM', # Explicitly set type for custom tests
        subjects_included=list(subject_ids_included) # Store the IDs of subjects with questions
    )

    # --- Create TestQuestionLink instances ---
    test_links = []
    for question in selected_questions:
        test_links.append(
            TestQuestionLink(
                test_id=generated_test_paper,
                question_id=question # question is a HeroQuestions instance here
            )
        )
    TestQuestionLink.objects.bulk_create(test_links) 

    # --- Serialize the results ---
    test_paper_serializer = GeneratedTestPaperSerializer(generated_test_paper)
    questions_serializer = HeroQuestionsWithoutAnswerSerializer(selected_questions, many=True)

    # --- Return the response ---
    return Response({
        'test_details': test_paper_serializer.data, 
        'questions': questions_serializer.data 
    }, status=status.HTTP_201_CREATED) 

def answers_match(user_ans, correct_ans):
    """
    Return True if two potentially nested JSON-compatible structures
    are equivalent, regardless of key order or whitespace.
    """
    # dumps with sorted keys and no extra spaces
    u = json.dumps(user_ans,    sort_keys=True, separators=(',', ':'))
    c = json.dumps(correct_ans, sort_keys=True, separators=(',', ':'))
    return u == c

class TestSubmissionView(views.APIView):
    """
    API endpoint for submitting answers for a generated test paper.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TestSubmissionSerializer # For input validation

    @swagger_auto_schema(
        # --- General ---
        operation_summary="Submit Test Answers",
        operation_description=(
            "Submits the user's answers for a specific generated test paper identified by its ID. "
            "Requires authentication. Compares submitted answers against correct answers, calculates "
            "the score based on marks defined for this test instance, and saves the attempt "
            "to the user's Test History."
        ),
        tags=["Tests", "Submissions"], # Helps organize endpoints in Swagger UI

        # --- Parameters (Path) ---
        manual_parameters=[
            openapi.Parameter(
                name='test_paper_id',
                in_=openapi.IN_PATH,
                description='The unique ID of the GeneratedTestPaper being submitted.',
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],

        # --- Request Body ---
        request_body=TestSubmissionSerializer, # Use the serializer to define the request body schema

        # --- Responses ---
        responses={
            # --- Success ---
            201: openapi.Response(
                description="CREATED: Test submitted successfully. Returns the detailed test result including score and breakdown per question.",
                schema=TestHistoryDetailSerializer # Use serializer for success response schema
            ),
            # --- Client Errors ---
            400: openapi.Response(
                description="BAD REQUEST: Invalid input data provided. This could be due to:\n"
                            "- Malformed JSON.\n"
                            "- Missing required fields (`answers`, `question_id`, `user_answer`).\n"
                            "- Incorrect data types.\n"
                            "- Mismatch between submitted answers and the actual questions in the test (e.g., missing answers, submitting answers for questions not in the test). Check the response body for specific details."
                # Note: drf-yasg doesn't have a direct 'inline_serializer'.
                # You'd typically define a specific ErrorSerializer if you need to show
                # a structured error response body, e.g., schema=MyStandardErrorSerializer
            ),
            401: openapi.Response(
                description="UNAUTHORIZED: Authentication credentials were not provided or are invalid. Please include a valid authentication token (e.g., Bearer token) in the request headers."
            ),
            # 403: openapi.Response( # Uncomment and adjust if you implement specific permission checks
            #    description="FORBIDDEN: User does not have permission to submit this specific test."
            # ),
            404: openapi.Response(
                description="NOT FOUND: The `GeneratedTestPaper` with the specified `test_paper_id` does not exist."
            ),
            # --- Server Errors (Implicitly handled, but can be documented) ---
            # 500: openapi.Response(description="INTERNAL SERVER ERROR: An unexpected error occurred on the server.")
        },

        # --- Security ---
        # drf-yasg often infers this from Authentication/Permission classes and global settings.
        # If 'BearerAuth' is defined in SWAGGER_SETTINGS['SECURITY_DEFINITIONS'] and
        # linked via SWAGGER_SETTINGS['SECURITY_REQUIREMENTS'], it should appear automatically
        # due to IsAuthenticated. Explicit definition here is less common.
        # security=[{"BearerAuth": []}] # Add this if inference isn't working as expected
    )

        # @transaction.atomic # Remove atomic from here if using the 'with' block below
    def post(self, request, test_paper_id, *args, **kwargs):
        # 1. Validate Input Data Structure using the basic submission serializer
        input_serializer = self.serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_input_data = input_serializer.validated_data
        submitted_answers_list = validated_input_data['answers'] # List of {'question_id': int, 'user_answer': json}
        time_taken = validated_input_data.get('time_taken', 0)

        # 2. Get the Generated Test Paper
        generated_test = get_object_or_404(GeneratedTestPaper, pk=test_paper_id)

        # 3. Get Questions and Marks for this Specific Test
        test_questions_links = TestQuestionLink.objects.filter(test_id=generated_test).select_related(
            'question_id__question'
        )
        if not test_questions_links.exists():
             return Response({"detail": "This test paper has no questions linked."}, status=status.HTTP_400_BAD_REQUEST)

        question_details_map = {}
        for link in test_questions_links:
            base_question = link.question_id.question
            hero_question = link.question_id
            question_details_map[base_question.id] = {
                'correct_answer': base_question.answer,
                'marks': hero_question.marks,
                'instance': base_question # Store the instance for later use
            }

        # 4. Process Answers and Calculate Score
        total_obtained_marks = 0
        processed_results = [] # To store data needed for ResultQuestionLink creation

        submitted_question_ids = {ans['question_id'] for ans in submitted_answers_list}
        test_question_ids = set(question_details_map.keys())

        # Check for mismatch
        if test_question_ids != submitted_question_ids:
             missing = test_question_ids - submitted_question_ids
             extra = submitted_question_ids - test_question_ids
             error_detail = {}
             if missing: error_detail["missing_answers_for_question_ids"] = sorted(list(missing))
             if extra: error_detail["extra_answers_for_question_ids"] = sorted(list(extra))
             return Response({
                 "detail": "Mismatch between submitted answers and test questions.",
                 **error_detail
                }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate score and prepare result data
        for submission in submitted_answers_list:
            question_id = submission['question_id']
            user_answer = submission['user_answer'] # This should be parsed JSON (dict/list/etc.)

            details = question_details_map.get(question_id)
            if not details:
                 # Should not happen if mismatch check passed, but good for safety
                 return Response({"detail": f"Invalid question ID {question_id} submitted."}, status=status.HTTP_400_BAD_REQUEST)

            correct_answer = details['correct_answer']
            # Perform comparison (adjust if complex JSON comparison needed)
            # is_correct = (user_answer == correct_answer)
            import pprint

            print("USER_ANSWER  >", type(user_answer), repr(user_answer))
            print("CORRECT_ANSWER >", type(correct_answer), repr(correct_answer))

            is_correct = answers_match(user_answer, correct_answer)

            if is_correct:
                total_obtained_marks += details['marks']

            processed_results.append({
                'question_instance': details['instance'], # The actual Questions object
                'user_answer': user_answer,
                'is_correct': is_correct
            })

        # 5. Create TestHistory and ResultQuestionLink records within a transaction
        try:
            with transaction.atomic():
                # Create TestHistory instance
                test_history = TestHistory.objects.create(
                    user=request.user,
                    total_marks=generated_test.total_marks,
                    obtained_marks=total_obtained_marks,
                    time=time_taken,
                    test_type=generated_test.test_type,
                    stream=generated_test.stream, # Pass the stream instance
                    subjects_included=generated_test.subjects_included
                )

                result_links_to_create = []
            for result_data in processed_results:
                # Get the marks for this question instance from the details map
                question_marks = question_details_map.get(result_data['question_instance'].id, {}).get('marks', 1) # Default marks to 1 if somehow not found

                result_links_to_create.append(
                    ResultQuestionLink(
                        result_id=test_history,
                        question_id=result_data['question_instance'],
                        user_answer=result_data['user_answer'],
                        is_correct=result_data['is_correct'],
                        # NEW: Save the marks
                        total_marks=question_marks,
                        marks_obtained=question_marks if result_data['is_correct'] else 0
                    )
                )

            # Use bulk_create for efficiency
            if result_links_to_create:
                ResultQuestionLink.objects.bulk_create(result_links_to_create)


        except Exception as e:
            # Log the exception e
            # logger.error(f"Error saving test submission for test {test_paper_id}: {e}")
            return Response({"detail": "An error occurred while saving the test results."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        # 6. Serialize the created TestHistory for the response
        # Use TestHistorySerializer (ensure it's set up for reading nested results correctly)
        response_serializer = TestHistoryDetailSerializer(test_history)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TestHistoryListView(generics.ListAPIView):
    """
    Provides a list of test summaries taken by the authenticated user.
    """
    serializer_class = TestHistorySummarySerializer
    permission_classes = [IsAuthenticated]
    # pagination_class = PageNumberPagination # Optional: Add pagination

    def get_queryset(self):
        # Order by most recent first
        return TestHistory.objects.filter(user=self.request.user).order_by('-created_at')

    @swagger_auto_schema(
        operation_summary="List User's Test History",
        responses={200: TestHistorySummarySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class TestHistoryDetailView(generics.RetrieveAPIView):
    """
    Provides detailed results for a specific test taken by the authenticated user.
    Includes each question, user answer, correct answer, and correctness.
    """
    serializer_class = TestHistoryDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = TestHistory.objects.prefetch_related(
        'question_links__question_id' # Prefetch for efficiency
    ).all()
    lookup_field = 'id' # Or 'pk'

    def get_queryset(self):
        # Ensure users can only retrieve their own history
        return super().get_queryset().filter(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Get Detailed Test Result",
        responses={
            200: TestHistoryDetailSerializer(),
            404: "Not Found (Test history does not exist or doesn't belong to user)"
         }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    


class OverallStatsView(APIView):
    """
    Provides overall performance statistics for the authenticated user
    across all tests taken.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get Overall User Statistics",
        responses={200: OverallStatsSerializer()}
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        history_qs = TestHistory.objects.filter(user=user)
        results_qs = ResultQuestionLink.objects.filter(result_id__user=user)

        # Calculate aggregates
        total_tests_taken = history_qs.count()
        overall_aggregates = results_qs.aggregate(
            total_attempted=Count('id'),
            total_correct=Sum(Case(When(is_correct=True, then=1), default=0, output_field=IntegerField())),
            sum_marks_possible=Sum('total_marks'),
            sum_marks_obtained=Sum('marks_obtained')
        )

        total_questions_attempted = overall_aggregates.get('total_attempted', 0) or 0
        total_correct_answers = overall_aggregates.get('total_correct', 0) or 0
        total_marks_possible = overall_aggregates.get('sum_marks_possible', 0) or 0
        total_marks_obtained = overall_aggregates.get('sum_marks_obtained', 0) or 0

        # Calculate percentages safely
        accuracy = (total_correct_answers * 100.0 / total_questions_attempted) if total_questions_attempted > 0 else 0.0
        score = (total_marks_obtained * 100.0 / total_marks_possible) if total_marks_possible > 0 else 0.0

        stats_data = {
            "total_tests_taken": total_tests_taken,
            "total_questions_attempted": total_questions_attempted,
            "total_correct_answers": total_correct_answers,
            "total_marks_possible": total_marks_possible,
            "total_marks_obtained": total_marks_obtained,
            "overall_accuracy_percentage": round(accuracy, 2),
            "overall_score_percentage": round(score, 2),
        }

        serializer = OverallStatsSerializer(instance=stats_data)
        return Response(serializer.data)


class BasePerformanceStatsView(APIView):
    """ Base class for performance stats views (Subject, Chapter, Topic) """
    permission_classes = [IsAuthenticated]
    grouping_field_id = None      # e.g., 'question_id__topic__chapter__sub_id'
    grouping_field_name = None    # e.g., 'question_id__topic__chapter__sub_id__subject_name'
    serializer_class = None       # e.g., SubjectPerformanceSerializer

    def get_stats(self, request):
        if not self.grouping_field_id or not self.serializer_class:
             raise NotImplementedError("Subclasses must define grouping fields and serializer_class")

        user = request.user
        # Base query - IMPORTANT: Assumes Questions.topic FK is populated
        stats = ResultQuestionLink.objects.filter(
            result_id__user=user,
            question_id__topic__isnull=False # Exclude questions without a topic link for reliable grouping
        ).values(
            self.grouping_field_id # Group by the ID field
        ).annotate(
            group_id=F(self.grouping_field_id), # Use F() to reference the field path
            group_name=F(self.grouping_field_name) if self.grouping_field_name else None, # Get name if defined
            attempted=Count('id'),
            correct=Sum(Case(When(is_correct=True, then=1), default=0, output_field=IntegerField())),
            total_marks_possible=Sum('total_marks'),
            marks_obtained=Sum('marks_obtained')
        ).values( # Select the final fields
            'group_id', 'group_name', 'attempted', 'correct',
            'total_marks_possible', 'marks_obtained'
        )

        # Calculate percentages in Python for clarity and division safety
        results = []
        for item in stats:
            accuracy = (item['correct'] * 100.0 / item['attempted']) if item['attempted'] > 0 else 0.0
            score = (item['marks_obtained'] * 100.0 / item['total_marks_possible']) if item['total_marks_possible'] > 0 else 0.0
            # Renaming group_id/group_name to match specific serializer fields
            # This could be cleaner using serializer source attribute if structure is consistent
            item_data = item.copy()
            item_data[self.serializer_class.Meta.fields[0]] = item_data.pop('group_id') # e.g., subject_id
            item_data[self.serializer_class.Meta.fields[1]] = item_data.pop('group_name') # e.g., subject_name
            item_data['accuracy_percentage'] = round(accuracy, 2)
            item_data['score_percentage'] = round(score, 2)
            results.append(item_data)

        return results

    def get(self, request, *args, **kwargs):
        stats_data = self.get_stats(request)
        serializer = self.serializer_class(instance=stats_data, many=True)
        return Response(serializer.data)


class SubjectPerformanceStatsView(BasePerformanceStatsView):
    """ Performance aggregated by Subject. """
    grouping_field_id = 'question_id__topic__chapter__sub_id'
    grouping_field_name = 'question_id__topic__chapter__sub_id__subject_name'
    serializer_class = SubjectPerformanceSerializer

    @swagger_auto_schema(
        operation_summary="Get User Performance by Subject",
        responses={200: SubjectPerformanceSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
         # This explicit definition helps drf-yasg find the serializer
        return super().get(request, *args, **kwargs)


class ChapterPerformanceStatsView(BasePerformanceStatsView):
    """ Performance aggregated by Chapter. """
    grouping_field_id = 'question_id__topic__chapter_id'
    grouping_field_name = 'question_id__topic__chapter__chapter_name'
    serializer_class = ChapterPerformanceSerializer # Need to define Meta in serializer

    @swagger_auto_schema(
        operation_summary="Get User Performance by Chapter",
        responses={200: ChapterPerformanceSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        # Add Meta class to ChapterPerformanceSerializer for field mapping if using base class logic
        # Or adjust the base class logic / override get_stats if needed
        # For now, assuming serializer setup matches the renaming logic in get_stats
        # We need to define Meta on the serializer for the renaming to work robustly
         return super().get(request, *args, **kwargs)


class TopicPerformanceStatsView(BasePerformanceStatsView):
    """ Performance aggregated by Topic. """
    grouping_field_id = 'question_id__topic_id'
    grouping_field_name = 'question_id__topic__topic_name'
    serializer_class = TopicPerformanceSerializer # Need to define Meta in serializer

    @swagger_auto_schema(
        operation_summary="Get User Performance by Topic",
        responses={200: TopicPerformanceSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        # Add Meta class to TopicPerformanceSerializer for field mapping
         return super().get(request, *args, **kwargs)
    





# --- Add Meta classes to performance serializers ---
# serializers.py

# ... other serializers ...







