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

class QuestionsSerializerV2(serializers.ModelSerializer):
    
    topic = TopicsSerializer(read_only=True, allow_null=True)

    
    topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Topics.objects.all(),
        source='topic', # This links topic_id input to the 'topic' model field for writing
        write_only=True,
        allow_null=True, # Matches Questions.topic (models.SET_NULL, null=True, blank=True)
        required=False
    )

    class Meta:
        model = Questions
        fields = ['id', 'topic', 'topic_id', 'question', 'options', 'answer']

class HeroQuestionsReadOnlySerializer(serializers.ModelSerializer):
    # Use the new QuestionsSerializer defined above for the 'question' field
    question = QuestionsSerializer(read_only=True)

    # For the 'topic' field of HeroQuestion, use YOUR TopicsSerializer
    topic = TopicsSerializer(read_only=True)

    # For the 'stream' field of HeroQuestion, use YOUR StreamsSerializer
    stream = StreamsSerializer(read_only=True)

    class Meta:
        model = HeroQuestions
        fields = ['id', 'topic', 'question', 'stream', 'marks', 'created_at', 'updated_at']


class CombinedHeroQuestionCreateUpdateSerializer(serializers.ModelSerializer):
    # Fields for the underlying Question model (these are for input only)
    question_text = serializers.CharField(write_only=True, help_text="Text of the base question.")
    question_options = serializers.JSONField(write_only=True, help_text="Options for the base question (JSON).")
    question_answer = serializers.JSONField(write_only=True, help_text="Answer for the base question (JSON).")
    question_base_topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Topics.objects.all(), # Refers to the ID of a Topic
        write_only=True,
        allow_null=True, # If Questions.topic can be null
        required=False,  # If Questions.topic can be blank
        source='question_base_topic', # For clarity in validated_data, see create/update
        help_text="ID of the topic for the base question itself (Questions.topic)."
    )

    # Fields for HeroQuestion Foreign Keys (input only, accepts IDs)
    hero_topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Topics.objects.all(), source='topic', write_only=True, # This sets HeroQuestions.topic
        help_text="ID of the topic for this HeroQuestion context (HeroQuestions.topic)."
    )
    stream_id = serializers.PrimaryKeyRelatedField(
        queryset=Streams.objects.all(), source='stream', write_only=True, # This sets HeroQuestions.stream
        help_text="ID of the stream for this HeroQuestion (HeroQuestions.stream)."
    )
    # 'marks' is a direct field on HeroQuestion, handled by ModelSerializer

    class Meta:
        model = HeroQuestions
        fields = [
            'id', # Read-only by default in this context
            'marks',
            # Write-only fields for creating/updating Question
            'question_text',
            'question_options',
            'question_answer',
            'question_base_topic_id',
            # Write-only fields for HeroQuestion FKs
            'hero_topic_id',
            'stream_id',
            # Read-only fields from HeroQuestion (for response after create/update)
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] # Explicitly mark these

    def create(self, validated_data):
        q_text = validated_data.pop('question_text')
        q_options = validated_data.pop('question_options')
        q_answer = validated_data.pop('question_answer')
        # 'question_base_topic' will be a Topic instance or None due to PrimaryKeyRelatedField's source
        q_base_topic_instance = validated_data.pop('question_base_topic', None)

        question_instance = Questions.objects.create(
            question=q_text,
            options=q_options,
            answer=q_answer,
            topic=q_base_topic_instance
        )

        # 'topic' and 'stream' in validated_data are Topic and Stream instances
        # resolved by hero_topic_id and stream_id due to their 'source' attribute.
        hero_question = HeroQuestions.objects.create(
            question=question_instance,
            **validated_data # Contains marks, topic (for HeroQ), stream
        )
        return hero_question

    def update(self, instance, validated_data):
        question_instance = instance.question

        question_instance.question = validated_data.get('question_text', question_instance.question)
        question_instance.options = validated_data.get('question_options', question_instance.options)
        question_instance.answer = validated_data.get('question_answer', question_instance.answer)

        # If 'question_base_topic_id' was provided, 'question_base_topic' will be in validated_data
        if 'question_base_topic' in validated_data:
            question_instance.topic = validated_data.get('question_base_topic')
        question_instance.save()

        # 'topic', 'stream' here refer to the HeroQuestion's fields, resolved from IDs
        instance.topic = validated_data.get('topic', instance.topic)
        instance.stream = validated_data.get('stream', instance.stream)
        instance.marks = validated_data.get('marks', instance.marks)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        After creating or updating, represent the instance using the
        HeroQuestionsReadOnlySerializer to show the full nested structure,
        which in turn uses YOUR TopicsSerializer and StreamsSerializer.
        """
        return HeroQuestionsReadOnlySerializer(instance, context=self.context).data
        

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
    user_answer = serializers.JSONField(required=True)

# New Serializer for the entire test submission
class TestSubmissionSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=AnswerSubmissionSerializer(),
        required=True,
        allow_empty=False # A submission must have answers
    )
    time_taken = serializers.IntegerField(required=False, default=0)

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
    class Meta: # Add Meta for field reference in base view
        fields = ['subject_id', 'subject_name', 'attempted', 'correct', 'total_marks_possible', 'marks_obtained', 'accuracy_percentage', 'score_percentage']

class ChapterPerformanceSerializer(BasePerformanceSerializer):
    chapter_id = serializers.IntegerField()
    chapter_name = serializers.CharField()
    # Example of including parent details if needed (adjust query/annotation accordingly)
    # subject_id = serializers.IntegerField(read_only=True)
    # subject_name = serializers.CharField(read_only=True)
    class Meta: # Add Meta
        fields = ['chapter_id', 'chapter_name', 'attempted', 'correct', 'total_marks_possible', 'marks_obtained', 'accuracy_percentage', 'score_percentage']

class TopicPerformanceSerializer(BasePerformanceSerializer):
    topic_id = serializers.IntegerField()
    topic_name = serializers.CharField()
    class Meta:
        fields = [
            'topic_id', 'topic_name',
            'attempted', 'correct',
            'total_marks_possible', 'marks_obtained',
            'accuracy_percentage', 'score_percentage'
        ]


class HeroQuestionWritePayloadSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=10000)
    options = serializers.ListField(child=serializers.CharField())
    answer = serializers.JSONField()
    # topic_id is handled by the parent HeroQuestionCreateUpdateSerializer

    # No create/update methods needed here as it's just for payload structure validation

# class HeroQuestionCreateUpdateSerializer(serializers.ModelSerializer):
#     topic_id = serializers.PrimaryKeyRelatedField(
#         queryset=Topics.objects.all(), source='topic',
#         help_text="ID of the Topic for this hero question instance."
#     )
#     stream_id = serializers.PrimaryKeyRelatedField(
#         queryset=Streams.objects.all(), source='stream',
#         help_text="ID of the Stream this hero question belongs to."
#     )
#     existing_question_id = serializers.PrimaryKeyRelatedField(
#         queryset=Questions.objects.all(), source='question', required=False, allow_null=True,
#         help_text="ID of an existing base question. If provided, 'new_question_details' will be ignored."
#     )
#     new_question_details = HeroQuestionWritePayloadSerializer(
#         required=False, write_only=True,
#         help_text="Details to create a new base question if 'existing_question_id' is not provided."
#     )
#     marks = serializers.IntegerField(help_text="Marks for this question (e.g., 1 or 2).")

#     class Meta:
#         model = HeroQuestions
#         fields = [
#             'topic_id', 'stream_id', 'marks',
#             'existing_question_id', 'new_question_details'
#         ]

#     def validate(self, data):
#         existing_question_obj = data.get('question') # 'question' is the source for existing_question_id
#         new_question_data = data.get('new_question_details')

#         if not existing_question_obj and not new_question_data:
#             raise serializers.ValidationError(
#                 "Either 'existing_question_id' or 'new_question_details' must be provided."
#             )
#         if existing_question_obj and new_question_data:
#             data.pop('new_question_details') # Prioritize existing_question_id
#         return data

#     def create(self, validated_data):
#         new_question_payload = validated_data.pop('new_question_details', None)
#         base_question = validated_data.get('question') # From existing_question_id
#         topic_obj = validated_data.get('topic')     # From topic_id
#         stream_obj = validated_data.get('stream')   # From stream_id
#         marks_val = validated_data.get('marks')

#         if not base_question and new_question_payload:
#             try:
#                 base_question = Questions.objects.create(
#                     topic=topic_obj, # Assign the topic from HeroQuestion to the new base Question
#                     question=new_question_payload['question'],
#                     options=new_question_payload['options'],
#                     answer=new_question_payload['answer']
#                 )
#             except IntegrityError as e: # E.g. if Questions.question has a unique constraint
#                 raise serializers.ValidationError({"new_question_details": f"Could not create base question (it might already exist or another DB constraint): {str(e)}"})
#             except Exception as e:
#                 raise serializers.ValidationError({"new_question_details": f"Error creating base question: {str(e)}"})
#         elif not base_question:
#              raise serializers.ValidationError("Base question could not be determined.")

#         try:
#             hero_question = HeroQuestions.objects.create(
#                 question=base_question,
#                 topic=topic_obj,
#                 stream=stream_obj,
#                 marks=marks_val
#             )
#         except IntegrityError:
#              # This assumes HeroQuestions has a unique_together on (question, topic, stream)
#              # If not, this specific error won't be raised for duplicates of this combination.
#              raise serializers.ValidationError({
#                  "detail": "This specific hero question (combination of base question, topic, and stream) already exists."
#              }, code="duplicate")
#         return hero_question

#     def update(self, instance, validated_data):
#         new_question_payload = validated_data.pop('new_question_details', None)
        
#         # If existing_question_id is provided in payload, it's mapped to 'question'
#         if 'question' in validated_data: 
#             instance.question = validated_data.get('question', instance.question)
#         # Note: Updating based on 'new_question_details' in an UPDATE operation is complex.
#         # It could mean:
#         # 1. Update the *linked* base question's details (better done via a /questions-base/{id} endpoint).
#         # 2. Create a *new* base question and re-link this HeroQuestion (less common for 'update').
#         # For simplicity, this 'update' primarily handles changing the linked base_question, topic, stream, marks.
#         # If 'new_question_details' is provided on update, it will be ignored if 'existing_question_id' is also present (due to validate method).
#         # If only 'new_question_details' is given on update without 'existing_question_id', it could imply creating a new base Q and re-linking.
#         # Let's clarify this: if new_question_details is provided on update AND no existing_question_id is, we create a new base question.
#         elif new_question_payload and not validated_data.get('question'): # if existing_question_id was NOT provided
#              try:
#                  base_question_topic = validated_data.get('topic', instance.topic)
#                  new_base_q = Questions.objects.create(
#                      topic=base_question_topic,
#                      question=new_question_payload['question'],
#                      options=new_question_payload['options'],
#                      answer=new_question_payload['answer']
#                  )
#                  instance.question = new_base_q # Re-link to the newly created base question
#              except IntegrityError as e:
#                  raise serializers.ValidationError({"new_question_details": f"Could not create new base question for update (it might already exist or another DB constraint): {str(e)}"})
#              except Exception as e:
#                  raise serializers.ValidationError({"new_question_details": f"Error creating new base question for update: {str(e)}"})


#         instance.topic = validated_data.get('topic', instance.topic)
#         instance.stream = validated_data.get('stream', instance.stream)
#         instance.marks = validated_data.get('marks', instance.marks)
#         instance.save()
#         return instance