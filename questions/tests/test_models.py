from django.test import TestCase
from accounts.models import User # Correct User import
from questions.models import (
    Subjects, Streams, Chapters, Topics, Questions, HeroQuestions,
    GeneratedTestPaper, TestQuestionLink, TestHistory, ResultQuestionLink
)
# No need to import json separately for direct assignment to JSONField

class ModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='password123'
        )
        cls.superuser = User.objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='password123'
        )
        cls.subject1 = Subjects.objects.create(subject_name="Math")
        cls.stream = Streams.objects.create(stream_name="Science")
        cls.chapter1 = Chapters.objects.create(sub_id=cls.subject1, chapter_name="Algebra")
        cls.topic1 = Topics.objects.create(chapter=cls.chapter1, topic_name="Linear Equations")

        cls.question1_options = {"option1":"3", "option2":"4", "option3":"5"}
        cls.question1_answer = {"correct":"4"} # Simple string answer
        cls.question1 = Questions.objects.create(
            topic=cls.topic1,
            question="What is 2+2?",
            options=cls.question1_options, # Assign list directly
            answer=cls.question1_answer    # Assign string/dict/list directly
        )

        cls.question2_options = [{"id": "a", "text": "Option A"}, {"id": "b", "text": "Option B"}]
        cls.question2_answer = {"id": "a"} # Dict answer
        cls.question2 = Questions.objects.create(
            topic=cls.topic1,
            question="Select Option A.",
            options=cls.question2_options,
            answer=cls.question2_answer
        )

        cls.hero_question1 = HeroQuestions.objects.create(
            topic=cls.topic1,
            question=cls.question1,
            stream=cls.stream,
            marks=1
        )
        cls.generated_test = GeneratedTestPaper.objects.create(
            stream=cls.stream,
            total_marks=10,
            total_questions=5,
            created_by=cls.user,
            test_type='CUSTOM',
            subjects_included=[cls.subject1.id] # List of IDs
        )
        TestQuestionLink.objects.create(test_id=cls.generated_test, question_id=cls.hero_question1)

        cls.test_history = TestHistory.objects.create(
            user=cls.user,
            total_marks=10,
            obtained_marks=5,
            stream=cls.stream,
            test_type='CUSTOM',
            subjects_included=[cls.subject1.id] # List of IDs
        )
        ResultQuestionLink.objects.create(
            result_id=cls.test_history,
            question_id=cls.question1,
            user_answer="4", # User's answer
            is_correct=True,
            marks_obtained=1,
            total_marks=1
        )

    def test_subject_creation_and_str(self):
        self.assertEqual(self.subject1.subject_name, "Math")
        self.assertEqual(str(self.subject1), "Math")

    def test_stream_creation_and_str(self):
        self.assertEqual(self.stream.stream_name, "Science")
        self.assertEqual(str(self.stream), "Science")

    def test_chapter_creation_and_str(self):
        self.assertEqual(self.chapter1.chapter_name, "Algebra")
        self.assertEqual(self.chapter1.sub_id, self.subject1)
        self.assertEqual(str(self.chapter1), "Math - Algebra")

    def test_topic_creation_and_str(self):
        self.assertEqual(self.topic1.topic_name, "Linear Equations")
        self.assertEqual(self.topic1.chapter, self.chapter1)
        self.assertEqual(str(self.topic1), "Math - Algebra - Linear Equations")

    def test_question_creation_json_fields(self):
        self.assertEqual(self.question1.question, "What is 2+2?")
        self.assertEqual(self.question1.options, self.question1_options) # Compare list directly
        self.assertEqual(self.question1.answer, self.question1_answer)   # Compare value directly
        self.assertEqual(str(self.question1), f"Q{self.question1.id}: What is 2+2?...")

        self.assertEqual(self.question2.options, self.question2_options)
        self.assertEqual(self.question2.answer, self.question2_answer)

    def test_hero_question_creation_and_str(self):
        self.assertEqual(self.hero_question1.marks, 1)
        self.assertEqual(self.hero_question1.question, self.question1)
        expected_str = f"HeroQ{self.hero_question1.id} (BaseQ: {self.question1.id}, Topic: {self.topic1.id}, Marks: 1)"
        self.assertEqual(str(self.hero_question1), expected_str)

    def test_generated_test_paper_creation(self):
        self.assertEqual(self.generated_test.created_by, self.user)
        self.assertEqual(self.generated_test.total_marks, 10)
        self.assertEqual(self.generated_test.subjects_included, [self.subject1.id])
        # Test __str__ if it's reliable or skip if it's problematic (e.g., concatenating objects)
        # For example, if fixed: self.assertEqual(str(self.generated_test), f"{self.stream.stream_name} ...")

    def test_test_question_link_creation(self):
        link = TestQuestionLink.objects.first()
        self.assertEqual(link.test_id, self.generated_test)
        self.assertEqual(link.question_id, self.hero_question1)

    def test_test_history_creation(self):
        self.assertEqual(self.test_history.user, self.user)
        self.assertEqual(self.test_history.obtained_marks, 5)
        self.assertEqual(self.test_history.subjects_included, [self.subject1.id])

    def test_result_question_link_creation(self):
        link = ResultQuestionLink.objects.filter(result_id=self.test_history).first()
        self.assertEqual(link.question_id, self.question1)
        self.assertEqual(link.user_answer, "4") # Stored as JSON but can be simple string
        self.assertTrue(link.is_correct)
        self.assertEqual(link.marks_obtained, 1)
        expected_str = f"ResultLink (History: {self.test_history.id}, BaseQ: {self.question1.id}, Correct: True)"
        self.assertEqual(str(link), expected_str)