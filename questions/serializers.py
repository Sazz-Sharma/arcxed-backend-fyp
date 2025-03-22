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
        
            
class TestHistorySerializer(serializers.ModelSerializer):
    questions = ResultQuestionLinkSerializer(many=True)

    class Meta:
        model = TestHistory
        fields = [
            'total_marks', 
            'obtained_marks', 
            'time', 
            'test_type', 
            'stream', 
            'subjects_included', 
            'questions'
        ]
        extra_kwargs = {
            'stream': {'required': True},
            'subjects_included': {'required': True}
        }

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        user = self.context['request'].user
        
        # Create UserResult
        user_result = TestHistory.objects.create(
            user=user,
            **validated_data
        )
        
        # Create ResultQuestionLink entries
        for q_data in questions_data:
            is_correct = False
            if q_data['user_answer'] == Questions.objects.get(id=q_data['question_id']['id']).answer:
                is_correct = True
            ResultQuestionLink.objects.create(
                result_id=user_result,
                question_id=q_data['question_id']['id'],  # Access the Questions instance
                user_answer=q_data['user_answer'],
                is_correct = is_correct
            )
        
        return user_result