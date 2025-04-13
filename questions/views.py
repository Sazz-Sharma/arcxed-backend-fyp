from django.shortcuts import render

from rest_framework import viewsets, status, views
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db import transaction 


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

# @swagger_auto_schema(
#     method='post',
#     request_body=CustomTestSerializer,
#     responses={
#         200: openapi.Response(
#             description="Custom test generated successfully",
#             schema=openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     'test_details': openapi.Schema(
#                         type=openapi.TYPE_OBJECT,
#                         properties={
#                             'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
#                             'total_marks': openapi.Schema(type=openapi.TYPE_INTEGER),
#                             'time_minutes': openapi.Schema(type=openapi.TYPE_INTEGER),
#                             'subjects_covered': openapi.Schema(
#                                 type=openapi.TYPE_ARRAY,
#                                 items=openapi.Schema(type=openapi.TYPE_INTEGER)
#                             )
#                         }
#                     ),
#                     'questions': openapi.Schema(
#                         type=openapi.TYPE_ARRAY,
#                         items=openapi.Schema(type=openapi.TYPE_OBJECT)
#                     )
#                 }
#             )
#         ),
#         400: "Invalid input data",
#         404: "Subject or chapter not found"
#     },
#     operation_description="Generate a custom test based on user-selected subjects, chapters, and number of questions.",
#     operation_summary="Create Custom Test"
# )
# @api_view(['POST'])
# def create_custom_test(request):
#     '''
#     Payload:
#                 {
#             "subjects": [
#                 {
#                 "subject_id": 1,
#                 "chapters": [
#                     {
#                     "chapter_id": 1,
#                     "num_questions": 5
#                     }
#                 ]
#                 }
#             ],
#             "time_minutes": 30
#             }
#     '''
#     serializer = CustomTestSerializer(data=request.data)
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     data = serializer.validated_data
#     selected_questions = []
#     total_marks = 0
#     stream = get_object_or_404(Streams, stream_name='IOE')  # Or make this configurable

#     for subject_data in data['subjects']:
#         subject = get_object_or_404(Subjects, id=subject_data['subject_id'])
        
#         for chapter_data in subject_data['chapters']:
#             chapter = get_object_or_404(Chapters, id=chapter_data['chapter_id'], sub_id=subject)
#             topics = Topics.objects.filter(chapter=chapter)
            
#             # Get random questions
#             questions = HeroQuestions.objects.filter(
#                 topic__in=topics,
#                 stream=stream
#             ).order_by('?')[:chapter_data['num_questions']]
            
#             if len(questions) < chapter_data['num_questions']:
#                 return Response({
#                     'error': f'Not enough questions for {subject.subject_name} - {chapter.chapter_name}'
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             selected_questions.extend(questions)
#             total_marks += sum(q.marks for q in questions)

#     serializer = HeroQuestionsWithoutAnswerSerializer(selected_questions, many=True)
    
#     return Response({
#         'test_details': {
#             'total_questions': len(selected_questions),
#             'total_marks': total_marks,
#             'time_minutes': data['time_minutes'],
#             'subjects_covered': [s['subject_id'] for s in data['subjects']]
#         },
#         'questions': serializer.data
#     })
        



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

                    # Option B: Reference generated component schemas (BEST if available)
                    # Check your /swagger.json or /schema endpoint to see if drf-yasg created these:
                    # 'test_details': openapi.Schema(ref='#/components/schemas/GeneratedTestPaper'),
                    # 'questions': openapi.Schema(
                    #     type=openapi.TYPE_ARRAY,
                    #     items=openapi.Schema(ref='#/components/schemas/HeroQuestionsWithoutAnswer')
                    # )

                    # Option C: Try passing the serializer directly (might work depending on drf-yasg version/config)
                    # 'test_details': GeneratedTestPaperSerializer(),
                    # 'questions': HeroQuestionsWithoutAnswerSerializer(many=True)
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
    TestQuestionLink.objects.bulk_create(test_links) # More efficient for multiple links

    # --- Serialize the results ---
    test_paper_serializer = GeneratedTestPaperSerializer(generated_test_paper)
    questions_serializer = HeroQuestionsWithoutAnswerSerializer(selected_questions, many=True)

    # --- Return the response ---
    return Response({
        'test_details': test_paper_serializer.data, # Contains the created test paper info (including its ID)
        'questions': questions_serializer.data # Contains the questions for the frontend to display
    }, status=status.HTTP_201_CREATED) # Use 201 Created status code


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
                schema=TestHistorySerializer # Use serializer for success response schema
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
            is_correct = (user_answer == correct_answer)

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

                # Create ResultQuestionLink entries
                result_links_to_create = []
                for result_data in processed_results:
                    result_links_to_create.append(
                        ResultQuestionLink(
                            result_id=test_history, # Link to the history instance
                            question_id=result_data['question_instance'], # Link to the question instance
                            user_answer=result_data['user_answer'],
                            is_correct=result_data['is_correct']
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
        response_serializer = TestHistorySerializer(test_history)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
