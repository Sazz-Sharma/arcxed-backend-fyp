from django.test import TestCase
from accounts.models import User
from questions.models import Subjects, Streams, Chapters, Topics, Questions, HeroQuestions, GeneratedTestPaper, TestHistory, ResultQuestionLink
from questions.serializers import (
    SubjectsSerializer, StreamsSerializer, ChaptersSerializer, TopicsSerializer,
    QuestionsSerializer, HeroQuestionsSerializer, HeroQuestionsWithoutAnswerSerializer,
    CustomTestSerializer, GeneratedTestPaperSerializer, TestSubmissionSerializer,
    AnswerSubmissionSerializer, TestHistoryDetailSerializer, TestHistorySummarySerializer,
    OverallStatsSerializer, SubjectPerformanceSerializer, ChapterPerformanceSerializer,
    TopicPerformanceSerializer, HeroQuestionCreateUpdateSerializer
)
import json

class SerializerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email = "testuser@gmail.com", username='testuser', password='password123')
        cls.subject = Subjects.objects.create(subject_name="Chemistry")
        cls.stream = Streams.objects.create(stream_name="Engineering")
        cls.chapter = Chapters.objects.create(sub_id=cls.subject, chapter_name="Organic")
        cls.topic = Topics.objects.create(chapter=cls.chapter, topic_name="Alkanes")
        cls.base_question = Questions.objects.create(
            topic=cls.topic,
            question="What is CH4?",
            options=["Methane", "Ethane"],
            answer="Methane"
        )
        cls.hero_question = HeroQuestions.objects.create(
            topic=cls.topic,
            question=cls.base_question,
            stream=cls.stream,
            marks=2
        )

    def test_subjects_serializer(self):
        serializer = SubjectsSerializer(instance=self.subject)
        self.assertEqual(serializer.data['subject_name'], "Chemistry")

    def test_streams_serializer(self):
        serializer = StreamsSerializer(instance=self.stream)
        self.assertEqual(serializer.data['stream_name'], "Engineering")

    def test_hero_question_create_update_serializer_validate_new(self):
        data = {
            "topic_id": self.topic.id,
            "stream_id": self.stream.id,
            "marks": 1,
            "new_question_details": {
                "question": "New Q",
                "options": ["A", "B"],
                "answer": "A"
            }
        }
        serializer = HeroQuestionCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_hero_question_create_update_serializer_validate_existing(self):
        data = {
            "topic_id": self.topic.id,
            "stream_id": self.stream.id,
            "marks": 1,
            "existing_question_id": self.base_question.id
        }
        serializer = HeroQuestionCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_hero_question_create_update_serializer_validate_both(self):
        # Should prioritize existing, new_question_details should be popped
        data = {
            "topic_id": self.topic.id,
            "stream_id": self.stream.id,
            "marks": 1,
            "existing_question_id": self.base_question.id,
            "new_question_details": {
                "question": "New Q",
                "options": ["A", "B"],
                "answer": "A"
            }
        }
        serializer = HeroQuestionCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('new_question_details', serializer.validated_data)

    def test_hero_question_create_update_serializer_validate_neither_fails(self):
        data = {
            "topic_id": self.topic.id,
            "stream_id": self.stream.id,
            "marks": 1,
        }
        serializer = HeroQuestionCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Either 'existing_question_id' or 'new_question_details' must be provided.", str(serializer.errors))

    def test_hero_question_create_update_serializer_create_with_new_question(self):
        data = {
            "topic_id": self.topic.id,
            "stream_id": self.stream.id,
            "marks": 1,
            "new_question_details": {
                "question": "What is C2H6?",
                "options": ["Methane", "Ethane"],
                "answer": "Ethane"
            }
        }
        serializer = HeroQuestionCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        questions_before = Questions.objects.count()
        hero_questions_before = HeroQuestions.objects.count()
        
        hero_q = serializer.save()

        self.assertEqual(Questions.objects.count(), questions_before + 1)
        self.assertEqual(HeroQuestions.objects.count(), hero_questions_before + 1)
        self.assertEqual(hero_q.question.question, "What is C2H6?")
        self.assertEqual(hero_q.marks, 1)
        self.assertEqual(hero_q.topic, self.topic)
        self.assertEqual(hero_q.question.topic, self.topic) # Ensure base question is linked to topic

    def test_hero_question_create_update_serializer_create_with_existing_question(self):
        data = {
            "topic_id": self.topic.id,
            "stream_id": self.stream.id,
            "marks": 3,
            "existing_question_id": self.base_question.id
        }
        serializer = HeroQuestionCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        questions_before = Questions.objects.count()
        hero_questions_before = HeroQuestions.objects.count()

        hero_q = serializer.save()

        self.assertEqual(Questions.objects.count(), questions_before) # No new base question
        self.assertEqual(HeroQuestions.objects.count(), hero_questions_before + 1)
        self.assertEqual(hero_q.question, self.base_question)
        self.assertEqual(hero_q.marks, 3)

    def test_custom_test_serializer_valid(self):
        data = {
            "subjects": [
                {
                    "subject_id": self.subject.id,
                    "chapters": [
                        {"chapter_id": self.chapter.id, "num_questions": 2}
                    ]
                }
            ],
            "time_minutes": 30
        }
        serializer = CustomTestSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_test_submission_serializer_valid(self):
        data = {
            "answers": [
                {"question_id": self.base_question.id, "user_answer": "Methane"}
            ],
            "time_taken": 120
        }
        serializer = TestSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_test_history_summary_serializer(self):
        history = TestHistory.objects.create(
            user=self.user, stream=self.stream, total_marks=100, obtained_marks=75, test_type="MOCK"
        )
        serializer = TestHistorySummarySerializer(instance=history)
        data = serializer.data
        self.assertEqual(data['stream_name'], self.stream.stream_name)
        self.assertEqual(data['score_percentage'], 75.0)

    def test_overall_stats_serializer(self):
        data = {
            "total_tests_taken": 5,
            "total_questions_attempted": 50,
            "total_correct_answers": 25,
            "total_marks_possible": 100,
            "total_marks_obtained": 50,
            "overall_accuracy_percentage": 50.0,
            "overall_score_percentage": 50.0,
        }
        serializer = OverallStatsSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    # Similar tests can be written for SubjectPerformanceSerializer, ChapterPerformanceSerializer, TopicPerformanceSerializer
    def test_subject_performance_serializer(self):
        data = {
            "subject_id": self.subject.id,
            "subject_name": self.subject.subject_name,
            "attempted": 10,
            "correct": 5,
            "total_marks_possible": 20,
            "marks_obtained": 10,
            "accuracy_percentage": 50.0,
            "score_percentage": 50.0
        }
        serializer = SubjectPerformanceSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_hero_questions_without_answer_serializer(self):
        serializer = HeroQuestionsWithoutAnswerSerializer(instance=self.hero_question)
        self.assertNotIn('answer', serializer.data['question'])
        self.assertIn('options', serializer.data['question'])
        self.assertEqual(serializer.data['question']['question'], self.base_question.question)