# questions/filters.py
import django_filters
from .models import HeroQuestions, Subjects, Chapters, Topics, Streams

class HeroQuestionFilter(django_filters.FilterSet):
    subject = django_filters.ModelChoiceFilter(
        field_name='topic__chapter__sub_id',
        queryset=Subjects.objects.all(),
        label='Subject ID'
    )
    chapter = django_filters.ModelChoiceFilter(
        field_name='topic__chapter',
        queryset=Chapters.objects.all(),
        label='Chapter ID'
    )
    topic = django_filters.ModelChoiceFilter(
        field_name='topic',
        queryset=Topics.objects.all(),
        label='Topic ID'
    )
    stream = django_filters.ModelChoiceFilter(
        field_name='stream',
        queryset=Streams.objects.all(), # Use Streams.objects.all()
        label='Stream ID'
    )
    marks = django_filters.NumberFilter(field_name='marks', lookup_expr='exact')
    question_text = django_filters.CharFilter(
        field_name='question__question',
        lookup_expr='icontains',
        label='Question Text (contains)'
    )
    # Filter by base question ID
    question_id = django_filters.NumberFilter(
        field_name='question__id', # Filter by the ID of the linked base Question
        label='Base Question ID'
    )

    class Meta:
        model = HeroQuestions
        fields = ['subject', 'chapter', 'topic', 'stream', 'marks', 'question_text', 'question_id']