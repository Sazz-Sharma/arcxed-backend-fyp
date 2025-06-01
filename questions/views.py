from django.shortcuts import render
from rest_framework import viewsets, status, views, generics
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser, IsSuperUserOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes, action
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
    permission_classes = [IsSuperUser]

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


class CombinedHeroQuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Hero Questions along with their base Question data.

    - POST: Creates a Hero Question and its underlying base Question in one request.
    - POST (/bulk-create/): Creates multiple Hero Questions and their base Questions.
    - GET: Retrieves Hero Questions with full details, including nested Question,
           Topic (for HeroQuestion), and Stream objects.
    - PUT/PATCH: Updates a Hero Question and/or its underlying base Question.
    - DELETE: Deletes a Hero Question (and its base Question if CASCADE is set).

    The representation of related Topic and Stream objects in API responses
    (e.g., in GET requests or after a POST/PUT) will use your existing
    TopicsSerializer and StreamsSerializer.
    """
    permission_classes = [IsSuperUser]
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
    
    @action(detail=False, methods=['post'], url_path='bulk-create', url_name='heroquestion-bulk-create')
    @swagger_auto_schema(
        operation_summary="Bulk create Combined Hero Questions",
        operation_description=(
            "Creates multiple Hero Questions and their underlying base Questions simultaneously. "
            "Provide a list of question objects in the request body. Each object should conform "
            "to the structure expected by the single create endpoint.\n"
            "The response will be a list of the newly created HeroQuestions, with nested objects "
            "formatted using HeroQuestionsReadOnlySerializer."
        ),
        request_body=CombinedHeroQuestionCreateUpdateSerializer(many=True), # Expects a list
        responses={
            201: HeroQuestionsReadOnlySerializer(many=True), # Returns a list
            400: "Validation Error: Check input data. If one item fails, the entire batch is rolled back."
        }
    )
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True) # Key: many=True
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic(): # Wrap in a transaction
                self.perform_bulk_create(serializer)
        except Exception as e:
            # You might want to log the error `e` here
            return Response(
                {"detail": f"An error occurred during bulk creation: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        headers = self.get_success_headers(serializer.data)
        # serializer.data will be a list, each item formatted by 
        # CombinedHeroQuestionCreateUpdateSerializer's to_representation
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_bulk_create(self, serializer):
        """
        Hook for saving a list of object instances.
        """
        serializer.save() # This will call serializer.child.create() for each item


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
    



from questions.faiss_engine.question_vectorizer import _qv

class QuestionSimilarityInputSerializer(serializers.Serializer):
    question = serializers.CharField(help_text="Text to check for similarity")

class QuestionSimilarityAPIView(APIView):
    @swagger_auto_schema(
        operation_summary='Retrieve similar questions',
        request_body=QuestionSimilarityInputSerializer,
        responses={
            200: openapi.Response(
                description='List of similar questions with full data and scores',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'similar': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'question': openapi.Schema(type=openapi.TYPE_OBJECT),
                                    'score': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
                                }
                            )
                        )
                    }
                )
            ),
            400: 'Bad Request'
        }
    )
    def post(self, request):
        serializer = QuestionSimilarityInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question_text = serializer.validated_data['question']

        # Run similarity pipeline
        raw_results = _qv.query(question_text, filter_k=50, rerank_k=5)

        # Build full response items
        similar = []
        for qid, _, score in raw_results:
            try:
                question_obj = Questions.objects.get(id=qid)
                serialized = QuestionsWithoutAnswerSerializer(question_obj)
                similar.append({
                    'question': serialized.data,
                    'score': score
                })
            except Questions.DoesNotExist:
                continue

        return Response({'similar': similar}, status=status.HTTP_200_OK)



# try:
#     from study_plan.main import (
#         GenerateQuestionFlow,
#         MakeStudyPlanFlow,
#         ExplainAnswerFlow,
#         EvaluateUserFlow,
#         SYLLABUS # Import the SYLLABUS constant
#     )
#     print("Successfully imported study_plan flows and SYLLABUS constant.")
# except ImportError as e:
#     print(e)
#     # Fallback for local testing or if paths are set up differently, e.g. src is in PYTHONPATH
#     # This is less robust for deployment.
#     print(f"ImportError: {e}. Attempting alternative import assuming 'study_plan' is in PYTHONPATH.")
#     # from study_plan.main import (
#     #     GenerateQuestionFlow,
#     #     MakeStudyPlanFlow,
#     #     ExplainAnswerFlow,
#     #     EvaluateUserFlow,
#     #     SYLLABUS
#     # )
from study_plan.main import (
        GenerateQuestionFlow,
        MakeStudyPlanFlow,
        ExplainAnswerFlow,
        EvaluateUserFlow,
        SYLLABUS # Import the SYLLABUS constant
    )

from .serializers import (
    GenerateQuestionRequestSerializer, GenerateQuestionResponseSerializer,
    CreateStudyPlanRequestSerializer, CreateStudyPlanResponseSerializer,
    ExplainAnswerRequestSerializer, ExplainAnswerResponseSerializer,
    EvaluateUserRequestSerializer, EvaluateUserResponseSerializer
)




class GenerateQuestionsAPIView(APIView):
    """
    Generates tailored questions for a user based on their current proficiency levels.
    The AI analyzes the user's `current_level` across subjects and chapters to create
    questions that are appropriately challenging and relevant to their learning needs.
    """
    @swagger_auto_schema(
        operation_summary="Generate Assessment Questions",
        operation_description="""Takes the user's current understanding level per subject/chapter and generates a set of questions.
        The syllabus is typically predefined in the system, but can be overridden if needed (though not implemented in this request serializer version).""",
        request_body=GenerateQuestionRequestSerializer,
        responses={
            200: GenerateQuestionResponseSerializer,
            400: "Bad Request - Invalid input data"
        },
        tags=['Assessment & Study Plan']
    )
    def post(self, request, *args, **kwargs):
        serializer = GenerateQuestionRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            flow = GenerateQuestionFlow()
            result_state = flow.generate_question_task(
                current_level=data['current_level'],
                syllabus=SYLLABUS # Or data.get('syllabus', SYLLABUS) if you implement override
            )
            response_serializer = GenerateQuestionResponseSerializer(data=result_state.dict()) # Use .dict() for Pydantic models
            if response_serializer.is_valid(): # Validate response serialization if complex
                 return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Should not happen if Pydantic model matches serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateStudyPlanAPIView(APIView):
    """
    Creates a personalized study plan for the user.
    This plan is based on their `current_level` of understanding and their performance
    on a set of `answered_questions`. The AI identifies areas needing improvement
    and suggests a path forward.
    """
    @swagger_auto_schema(
        operation_summary="Create Personalized Study Plan",
        operation_description="""Generates a study plan based on the user's current knowledge level and their answers to a set of questions.
        The AI will analyze these inputs to suggest topics to focus on.""",
        request_body=CreateStudyPlanRequestSerializer,
        responses={
            200: CreateStudyPlanResponseSerializer,
            400: "Bad Request - Invalid input data"
        },
        tags=['Assessment & Study Plan']
    )
    def post(self, request, *args, **kwargs):
        serializer = CreateStudyPlanRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            flow = MakeStudyPlanFlow()
            result_state = flow.make_study_plan_task(
                current_level=data['current_level'],
                answered_questions=data['answered_questions'],
                syllabus=SYLLABUS # Or data.get('syllabus', SYLLABUS)
            )
            response_serializer = CreateStudyPlanResponseSerializer(data=result_state.dict())
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExplainAnswerAPIView(APIView):
    """
    Provides a detailed explanation for a specific question.
    Given the `question_text`, `options`, and the `correct_answer`, the AI generates
    an explanation to help the user understand the underlying concepts and why the
    answer is correct.
    """
    @swagger_auto_schema(
        operation_summary="Explain an Answer",
        operation_description="Provides an AI-generated explanation for a given question, its options, and the correct answer.",
        request_body=ExplainAnswerRequestSerializer,
        responses={
            200: ExplainAnswerResponseSerializer,
            400: "Bad Request - Invalid input data"
            # 404: "Not Found - If fetching question by ID and not found" (if you implement ID fetching)
        },
        tags=['Learning Tools']
    )
    def post(self, request, *args, **kwargs):
        serializer = ExplainAnswerRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            flow = ExplainAnswerFlow()
            result_state = flow.explain_answer_task(
                question=data['question_text'],
                options=data['options'],
                correct_answer=data['correct_answer']
            )
            response_serializer = ExplainAnswerResponseSerializer(data=result_state.dict())
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EvaluateUserAPIView(APIView):
    """
    Evaluates user performance based on provided data.
    The `evaluation_type` (e.g., 'topic', 'overall') determines the scope of analysis.
    The `performance_data` contains metrics like attempts, corrects, and scores.
    The AI provides an assessment of this performance.
    """
    @swagger_auto_schema(
        operation_summary="Evaluate User Performance",
        operation_description="Analyzes user performance data (e.g., scores, accuracy per topic) and provides an AI-generated evaluation.",
        request_body=EvaluateUserRequestSerializer,
        responses={
            200: EvaluateUserResponseSerializer,
            400: "Bad Request - Invalid input data"
        },
        tags=['User Performance']
    )
    def post(self, request, *args, **kwargs):
        serializer = EvaluateUserRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            flow = EvaluateUserFlow()
            result_state = flow.evaluate_user_task(
                evaluation_type=data['evaluation_type'],
                performance_data=data['performance_data']
            )
            response_serializer = EvaluateUserResponseSerializer(data=result_state.dict())
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)