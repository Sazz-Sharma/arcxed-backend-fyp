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
        exclude = ('answer',)


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
    
    
class TestAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=True)
    user_answer = serializers.CharField(required=True)

class TestResultSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=TestAnswerSerializer(),
        required=True
    )