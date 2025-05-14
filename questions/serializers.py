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

class QuestionWithAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['id', 'question', 'options', 'answer'] # Include answer
    
    
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

# class ResultQuestionLinkSerializer(serializers.ModelSerializer):
#     # Keep this as is - it's used for *outputting* results mainly,
#     # but also informs the structure needed for nested writes.
#     # When creating, we'll provide the 'question_id' as an integer PK.
#     question = QuestionsSerializer(read_only=True) # Show full question detail on result retrieval
#     question_id = serializers.PrimaryKeyRelatedField(
#         queryset=Questions.objects.all(),
#         write_only=True # Use this field for writing
#     )

#     class Meta:
#         model = ResultQuestionLink
#         # Include 'question' for reading, 'question_id' is implicitly used for writing
#         fields = ['question_id', 'user_answer', 'is_correct', 'question']
#         read_only_fields = ['is_correct', 'question'] # is_correct is calculated server-side

class ResultQuestionLinkDetailSerializer(serializers.ModelSerializer):
    # Show nested question object WITH the correct answer
    question_details = QuestionWithAnswerSerializer(source='question_id', read_only=True)

    class Meta:
        model = ResultQuestionLink
        fields = [
            # 'id', # Optional: ID of the link itself
            'question_details', # Nested question data + correct answer
            'user_answer',
            'is_correct',
            'marks_obtained',
            'total_marks',
        ]

class TestHistoryDetailSerializer(serializers.ModelSerializer):
    # Use the new ResultQuestionLinkDetailSerializer for the nested questions
    question_links = ResultQuestionLinkDetailSerializer(many=True, read_only=True) # Use the related_name 'question_links'
    stream_details = StreamsSerializer(source='stream', read_only=True)
    user_details = serializers.StringRelatedField(source='user', read_only=True)
    score_percentage = serializers.SerializerMethodField() # Added percentage here too

    class Meta:
        model = TestHistory
        fields = [
            'id', 'user_details', 'total_marks', 'obtained_marks', 'score_percentage',
            'created_at', 'updated_at', 'time', 'test_type',
            'stream_details', 'subjects_included', 'question_links' # Use 'question_links' here
        ]

    def get_score_percentage(self, obj):
        if obj.total_marks and obj.total_marks > 0:
            return round((obj.obtained_marks / obj.total_marks) * 100, 2)
        return 0.0


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


class TestHistorySummarySerializer(serializers.ModelSerializer):
    stream_name = serializers.CharField(source='stream.stream_name', read_only=True)
    # Calculate score percentage on the fly
    score_percentage = serializers.SerializerMethodField()

    class Meta:
        model = TestHistory
        fields = [
            'id',
            'created_at',
            'test_type',
            'stream_name',
            'total_marks',
            'obtained_marks',
            'score_percentage',
        ]

    def get_score_percentage(self, obj):
        if obj.total_marks and obj.total_marks > 0:
            return round((obj.obtained_marks / obj.total_marks) * 100, 2)
        return 0.0



class OverallStatsSerializer(serializers.Serializer):
    total_tests_taken = serializers.IntegerField()
    total_questions_attempted = serializers.IntegerField()
    total_correct_answers = serializers.IntegerField()
    total_marks_possible = serializers.IntegerField()
    total_marks_obtained = serializers.IntegerField()
    overall_accuracy_percentage = serializers.FloatField()
    overall_score_percentage = serializers.FloatField()

class BasePerformanceSerializer(serializers.Serializer):
    """Base for Subject/Chapter/Topic performance"""
    attempted = serializers.IntegerField()
    correct = serializers.IntegerField()
    total_marks_possible = serializers.IntegerField()
    marks_obtained = serializers.IntegerField()
    accuracy_percentage = serializers.FloatField()
    score_percentage = serializers.FloatField()

class SubjectPerformanceSerializer(BasePerformanceSerializer):
    subject_id = serializers.IntegerField()
    subject_name = serializers.CharField()

class ChapterPerformanceSerializer(BasePerformanceSerializer):
    chapter_id = serializers.IntegerField()
    chapter_name = serializers.CharField()
    # Optionally include parent subject info
    subject_id = serializers.IntegerField(source='topic__chapter__sub_id__id') # Example source path
    subject_name = serializers.CharField(source='topic__chapter__sub_id__subject_name') # Example source path

class TopicPerformanceSerializer(BasePerformanceSerializer):
    topic_id = serializers.IntegerField()
    topic_name = serializers.CharField()
    # Optionally include parent chapter/subject info
    chapter_id = serializers.IntegerField(source='topic__chapter_id')
    chapter_name = serializers.CharField(source='topic__chapter__chapter_name')
    subject_id = serializers.IntegerField(source='topic__chapter__sub_id__id')
    subject_name = serializers.CharField(source='topic__chapter__sub_id__subject_name')

