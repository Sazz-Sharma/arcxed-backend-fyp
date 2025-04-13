from rest_framework import serializers
from .models import *

class SubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = '__all__'

class StreamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streams
        fields = '__all__'

class ChaptersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapters
        fields = '__all__'



class TopicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topics
        fields = '__all__'

class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = '__all__'

class HeroQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroQuestions
        fields = '__all__'

class QuestionsWithoutAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        exclude = ('answer',)

class HeroQuestionsWithoutAnswerSerializer(serializers.ModelSerializer):
    question = QuestionsWithoutAnswerSerializer()
    class Meta:
        model = HeroQuestions
        fields = '__all__'

class ChapterRequestSerializer(serializers.Serializer):
    chapter_id = serializers.IntegerField(min_value=1, required=True)
    num_questions = serializers.IntegerField(min_value=1, required=True)

class SubjectRequestSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField(min_value=1, required=True)
    chapters = serializers.ListField(
        child=ChapterRequestSerializer(),
        required=True
    )

class CustomTestSerializer(serializers.Serializer):
    subjects = serializers.ListField(
        child=SubjectRequestSerializer(),
        required=True
    )
    time_minutes = serializers.IntegerField(min_value=1, required=True)
    
    
    
# class TestAnswerSerializer(serializers.Serializer):
#     question_id = serializers.IntegerField(required=True)
#     user_answer = serializers.CharField(required=True)

# class TestResultSerializer(serializers.Serializer):
#     answers = serializers.ListField(
#         child=TestAnswerSerializer(),
#         required=True
#     )

class ResultQuestionLinkSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Questions.objects.all(),
        source='question_id.id'  # Maps to the question_id ForeignKey
    )

    class Meta:
        model = ResultQuestionLink
        fields = ['question_id', 'user_answer', 'is_correct']


class GeneratedTestPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedTestPaper
        fields = '__all__'
    
    def get_questions(self, obj):
        questions = TestQuestionLink.objects.filter(test_id=obj)
        return HeroQuestionsWithoutAnswerSerializer(questions, many=True).data
        
            
# class TestHistorySerializer(serializers.ModelSerializer):
#     questions = ResultQuestionLinkSerializer(many=True)

#     class Meta:
#         model = TestHistory
#         fields = [
#             'total_marks', 
#             'obtained_marks', 
#             'time', 
#             'test_type', 
#             'stream', 
#             'subjects_included', 
#             'questions'
#         ]
#         extra_kwargs = {
#             'stream': {'required': True},
#             'subjects_included': {'required': True}
#         }

#     def create(self, validated_data):
#         questions_data = validated_data.pop('questions')
#         user = self.context['request'].user
        
#         # Create UserResult
#         user_result = TestHistory.objects.create(
#             user=user,
#             **validated_data
#         )
        
#         # Create ResultQuestionLink entries
#         for q_data in questions_data:
#             is_correct = False
#             if q_data['user_answer'] == Questions.objects.get(id=q_data['question_id']['id']).answer:
#                 is_correct = True
#             ResultQuestionLink.objects.create(
#                 result_id=user_result,
#                 question_id=q_data['question_id']['id'],  # Access the Questions instance
#                 user_answer=q_data['user_answer'],
#                 is_correct = is_correct
#             )
        
#         return user_result


class TestHistorySerializer(serializers.ModelSerializer):
    # Use SerializerMethodField to fetch related questions
    questions = serializers.SerializerMethodField()
    stream_details = StreamsSerializer(source='stream', read_only=True)
    user_details = serializers.StringRelatedField(source='user', read_only=True)

    class Meta:
        model = TestHistory
        fields = [
            'id',
            'user',
            'user_details',
            'total_marks',
            'obtained_marks',
            'created_at',
            'updated_at',
            'time',
            'test_type',
            'stream',
            'stream_details',
            'subjects_included',
            'questions',
        ]
        read_only_fields = [
            'id', 'user', 'user_details', 'obtained_marks', 'created_at',
            'updated_at', 'stream_details',
        ]

    def get_questions(self, obj):
        # Fetch related ResultQuestionLink objects and serialize them
        result_links = ResultQuestionLink.objects.filter(result_id=obj)
        return ResultQuestionLinkSerializer(result_links, many=True).data
    
class AnswerSubmissionSerializer(serializers.Serializer):
    # Use the ID of the base Question model for easier lookup of the correct answer
    question_id = serializers.IntegerField(required=True)
    # User's answer - Make sure the frontend sends data matching the structure
    # of the 'answer' JSONField in your Questions model (e.g., a string, a list, etc.)
    user_answer = serializers.JSONField(required=True)

# New Serializer for the entire test submission
class TestSubmissionSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=AnswerSubmissionSerializer(),
        required=True,
        allow_empty=False # A submission must have answers
    )
    # Optional: Frontend can send time spent in seconds or minutes
    time_taken = serializers.IntegerField(required=False, default=0)

# --- Modify TestHistorySerializer ---

class ResultQuestionLinkSerializer(serializers.ModelSerializer):
    # Keep this as is - it's used for *outputting* results mainly,
    # but also informs the structure needed for nested writes.
    # When creating, we'll provide the 'question_id' as an integer PK.
    question = QuestionsSerializer(read_only=True) # Show full question detail on result retrieval
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Questions.objects.all(),
        write_only=True # Use this field for writing
    )

    class Meta:
        model = ResultQuestionLink
        # Include 'question' for reading, 'question_id' is implicitly used for writing
        fields = ['question_id', 'user_answer', 'is_correct', 'question']
        read_only_fields = ['is_correct', 'question'] # is_correct is calculated server-side

class TestHistorySerializer(serializers.ModelSerializer):
    # Use SerializerMethodField to fetch related questions
    questions = serializers.SerializerMethodField()
    stream_details = StreamsSerializer(source='stream', read_only=True)
    user_details = serializers.StringRelatedField(source='user', read_only=True)

    class Meta:
        model = TestHistory
        fields = [
            'id',
            'user',
            'user_details',
            'total_marks',
            'obtained_marks',
            'created_at',
            'updated_at',
            'time',
            'test_type',
            'stream',
            'stream_details',
            'subjects_included',
            'questions',
        ]
        read_only_fields = [
            'id', 'user', 'user_details', 'obtained_marks', 'created_at',
            'updated_at', 'stream_details',
        ]

    def get_questions(self, obj):
        # Fetch related ResultQuestionLink objects and serialize them
        result_links = ResultQuestionLink.objects.filter(result_id=obj)
        return ResultQuestionLinkSerializer(result_links, many=True).data
    
    
class AnswerSubmissionSerializer(serializers.Serializer):
    # Use the ID of the base Question model for easier lookup of the correct answer
    question_id = serializers.IntegerField(required=True)
    # User's answer - Make sure the frontend sends data matching the structure
    # of the 'answer' JSONField in your Questions model (e.g., a string, a list, etc.)
    user_answer = serializers.JSONField(required=True)

# New Serializer for the entire test submission
class TestSubmissionSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=AnswerSubmissionSerializer(),
        required=True,
        allow_empty=False # A submission must have answers
    )
    # Optional: Frontend can send time spent in seconds or minutes
    time_taken = serializers.IntegerField(required=False, default=0)