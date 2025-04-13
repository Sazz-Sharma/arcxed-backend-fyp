from django.db import models
from accounts.models import User
# Create your models here.

class Subjects(models.Model):
    subject_name = models.CharField(max_length=100, unique=True)
    
class Streams(models.Model):
    stream_name = models.CharField(max_length=100,unique=True)

class Chapters(models.Model):
    sub_id = models.ForeignKey(Subjects, on_delete=models.PROTECT)
    chapter_name = models.CharField(max_length = 100, blank=False, null=False)

class Topics(models.Model):
    topic_name = models.CharField(max_length=100, null = False)
    chapter = models.ForeignKey(Chapters, null=False, on_delete=models.CASCADE)
    

class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField()
    options = models.JSONField()
    answer = models.JSONField()

class HeroQuestions(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    stream = models.ForeignKey(Streams, on_delete=models.CASCADE)
    marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
class GeneratedTestPaper(models.Model):
    id = models.AutoField(primary_key=True)
    stream = models.ForeignKey(Streams, on_delete=models.CASCADE)
    total_marks = models.IntegerField()
    total_questions = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    TEST_TYPE_CHOICES = [
        ('CUSTOM', 'custom'), 
        ('MOCK', 'mock'), 
    ]
    test_type = models.CharField(max_length=6, choices=TEST_TYPE_CHOICES, default='custom')
    subjects_included = models.JSONField(default=list)
    
    
    def __str__(self): 
        return self.stream + " " + self.created_at + " " + self.created_by
    
    def get_subjects(self):
        return self.questions.values_list('topic__chapter__sub_id__subject_name', flat=True).distinct()

    
class TestQuestionLink(models.Model):
    test_id = models.ForeignKey(GeneratedTestPaper, on_delete=models.CASCADE)
    question_id = models.ForeignKey(HeroQuestions, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.test_id + " " + self.question_id
    
class TestHistory(models.Model):
    TEST_TYPE_CHOICES = [
        ('CUSTOM', 'custom'), 
        ('MOCK', 'mock'), 
    ]
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_marks = models.IntegerField(default=0)
    obtained_marks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time = models.IntegerField(default=0)
    test_type = models.CharField(max_length=6, choices=TEST_TYPE_CHOICES, default='custom')
    stream = models.ForeignKey(Streams, on_delete=models.CASCADE, null = True)
    subjects_included = models.JSONField(default=list)


class ResultQuestionLink(models.Model):
    result_id = models.ForeignKey(TestHistory, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Questions, on_delete=models.CASCADE)
    # user_answer = models.TextField() # CHANGE THIS
    user_answer = models.JSONField() # TO THIS (Requires Django 3.1+ and appropriate DB support)
    is_correct = models.BooleanField()
    
    


