from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase # APIClient is part of APITestCase
from accounts.models import User # Correct User import
from questions.models import Subjects, Streams, Chapters, Topics, Questions, HeroQuestions
from questions.serializers import HeroQuestionsSerializer # For checking response structure

class BasicCRUDTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='testuser_crud@example.com',
            username='testuser_crud',
            password='password123'
        )
        cls.superuser = User.objects.create_superuser(
            email='admin_crud@example.com',
            username='adminuser_crud',
            password='password123'
        )

        cls.subject1 = Subjects.objects.create(subject_name="Mathematics")
        cls.stream1 = Streams.objects.create(stream_name="Science Stream")
        cls.chapter1 = Chapters.objects.create(sub_id=cls.subject1, chapter_name="Calculus")
        cls.topic1 = Topics.objects.create(chapter=cls.chapter1, topic_name="Differentiation")
        cls.base_q1_options = ["1", "0", "x"]
        cls.base_q1_answer = "1"
        cls.base_q1 = Questions.objects.create(
            topic=cls.topic1,
            question="What is dx/dx?",
            options=cls.base_q1_options,
            answer=cls.base_q1_answer
        )

    def test_list_subjects_unauthenticated_and_authenticated(self):
        url = reverse('subjects-list')
        # Unauthenticated (IsSuperUserOrReadOnly allows GET)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1) # Assuming pagination default

        # Authenticated normal user
        self.client.login(email='testuser_crud@example.com', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_subject_as_superuser(self):
        self.client.login(email='admin_crud@example.com', password='password123')
        url = reverse('subjects-list')
        data = {'subject_name': 'Physics'}
        response = self.client.post(url, data, format='json') # Use format='json' for POST/PUT
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subjects.objects.count(), 2)
        self.assertEqual(response.data['subject_name'], 'Physics')

    def test_create_subject_as_normal_user_forbidden(self):
        self.client.login(email='testuser_crud@example.com', password='password123')
        url = reverse('subjects-list')
        data = {'subject_name': 'Chemistry'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Similar tests for StreamsViewSet and ChaptersViewSet (can be added for completeness)

    def test_list_question_base(self):
        # Assuming QuestionViewSet has IsSuperUserOrReadOnly or similar
        self.client.login(email='testuser_crud@example.com', password='password123')
        url = reverse('question-base-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1) # Check if item is present

    def test_create_question_base_as_superuser(self):
        self.client.login(email='admin_crud@example.com', password='password123')
        url = reverse('question-base-list')
        payload = {
            "topic": self.topic1.id,
            "question": "What is integral of 1 dx?",
            "options": ["x+C", "1+C", "0+C"], # Send as list
            "answer": "x+C"  # Send as string
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Questions.objects.count(), 2)
        created_question = Questions.objects.get(id=response.data['id'])
        self.assertEqual(created_question.options, payload['options'])
        self.assertEqual(created_question.answer, payload['answer'])

    def test_list_hero_questions_with_filter(self):
        hero_q = HeroQuestions.objects.create(
            topic=self.topic1, question=self.base_q1, stream=self.stream1, marks=1
        )
        # Login as normal user, assuming HeroQuestionViewSet allows GET for authenticated
        self.client.login(email='testuser_crud@example.com', password='password123')
        url = reverse('hero-question-list') + f'?topic_id={self.topic1.id}' # Filter by topic_id
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], hero_q.id)
        self.assertEqual(response.data['results'][0]['marks'], 1)

    def test_create_hero_question_with_new_base_question_as_superuser(self):
        self.client.login(email='admin_crud@example.com', password='password123')
        url = reverse('hero-question-list')
        payload = {
            "topic_id": self.topic1.id,
            "stream_id": self.stream1.id,
            "marks": 2,
            "new_question_details": {
                "question": "A new hero question's base.",
                "options": ["Opt1", "Opt2"], # List
                "answer": {"choice": "Opt1"} # Dict
            }
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(HeroQuestions.objects.count(), 1)
        self.assertEqual(Questions.objects.count(), 2) # One from setUpTestData, one new
        
        hero_q_instance = HeroQuestions.objects.get(id=response.data['id'])
        self.assertEqual(hero_q_instance.question.question, payload['new_question_details']['question'])
        self.assertEqual(hero_q_instance.question.options, payload['new_question_details']['options'])
        self.assertEqual(hero_q_instance.question.answer, payload['new_question_details']['answer'])
        self.assertEqual(hero_q_instance.marks, 2)
        self.assertEqual(hero_q_instance.topic, self.topic1)
        self.assertEqual(hero_q_instance.question.topic, self.topic1) # Base question linked to HeroQ's topic

        # Check response uses HeroQuestionsSerializer (not HeroQuestionCreateUpdateSerializer)
        # HeroQuestionsSerializer should nest the full Question object (or QuestionsWithoutAnswerSerializer if that's intended for list/retrieve)
        self.assertIn('question', response.data) # Check if the 'question' field (FK to Questions) is serialized
        self.assertIsInstance(response.data['question'], dict) # It should be a serialized Question object
        self.assertEqual(response.data['question']['id'], hero_q_instance.question.id)
        self.assertEqual(response.data['question']['question'], payload['new_question_details']['question'])


    def test_create_hero_question_with_existing_base_question_as_superuser(self):
        self.client.login(email='admin_crud@example.com', password='password123')
        url = reverse('hero-question-list')
        payload = {
            "topic_id": self.topic1.id,
            "stream_id": self.stream1.id,
            "marks": 1,
            "existing_question_id": self.base_q1.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HeroQuestions.objects.count(), 1)
        self.assertEqual(Questions.objects.count(), 1) # No new base question
        hero_q_instance = HeroQuestions.objects.get(id=response.data['id'])
        self.assertEqual(hero_q_instance.question, self.base_q1)
        self.assertEqual(response.data['question']['id'], self.base_q1.id)


    def test_update_hero_question_as_superuser(self):
        self.client.login(email='admin_crud@example.com', password='password123')
        hero_q_to_update = HeroQuestions.objects.create(
            topic=self.topic1, question=self.base_q1, stream=self.stream1, marks=1
        )
        url = reverse('hero-question-detail', kwargs={'pk': hero_q_to_update.pk})
        
        new_topic = Topics.objects.create(chapter=self.chapter1, topic_name="Integration")
        new_stream = Streams.objects.create(stream_name="Arts Stream")
        new_base_q_options = ["A", "B", "C"]
        new_base_q_answer = "C"
        new_base_q = Questions.objects.create(
            topic=new_topic, question="Updated BaseQ?", options=new_base_q_options, answer=new_base_q_answer
        )

        payload = {
            "topic_id": new_topic.id,
            "stream_id": new_stream.id,
            "marks": 5,
            "existing_question_id": new_base_q.id # Change linked base question
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        
        hero_q_to_update.refresh_from_db()
        self.assertEqual(hero_q_to_update.marks, 5)
        self.assertEqual(hero_q_to_update.topic, new_topic)
        self.assertEqual(hero_q_to_update.stream, new_stream)
        self.assertEqual(hero_q_to_update.question, new_base_q)
        
        # Check response serializer (should be HeroQuestionsSerializer)
        self.assertEqual(response.data['marks'], 5)
        self.assertEqual(response.data['question']['id'], new_base_q.id)
        self.assertEqual(response.data['question']['question'], "Updated BaseQ?")