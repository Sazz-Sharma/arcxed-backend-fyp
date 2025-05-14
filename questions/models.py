from django.db import models
from accounts.models import User
# Create your models here.

class Subjects(models.Model):
    subject_name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.subject_name
    
class Streams(models.Model):
    stream_name = models.CharField(max_length=100,unique=True)
    def __str__(self): return self.stream_name


class Chapters(models.Model):
    sub_id = models.ForeignKey(Subjects, on_delete=models.PROTECT, related_name='chapters') # Added related_name
    chapter_name = models.CharField(max_length = 100, blank=False, null=False)
    # Add unique constraint if a chapter name should be unique within a subject
    # class Meta:
    #     unique_together = ('sub_id', 'chapter_name')
    def __str__(self): return f"{self.sub_id.subject_name} - {self.chapter_name}"


# class Topics(models.Model):
#     topic_name = models.CharField(max_length=100, null = False)
#     chapter = models.ForeignKey(Chapters, null=False, on_delete=models.CASCADE)
    
class Topics(models.Model):
    topic_name = models.CharField(max_length=100, null = False)
    chapter = models.ForeignKey(Chapters, null=False, on_delete=models.CASCADE)
    # Add unique constraint if a topic name should be unique within a chapter
    # class Meta:
    #     unique_together = ('topic_name', 'chapter')
    def __str__(self):
        return f"{self.chapter.sub_id.subject_name} - {self.chapter.chapter_name} - {self.topic_name}"


# class Questions(models.Model):
#     id = models.AutoField(primary_key=True)
#     question = models.TextField()
#     options = models.JSONField()
#     answer = models.JSONField()

class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    # Add a ForeignKey to link a question primarily to one Topic
    # This simplifies analysis significantly. Choose on_delete strategy (SET_NULL, PROTECT, CASCADE)
    topic = models.ForeignKey(Topics, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    question = models.TextField()
    options = models.JSONField()
    answer = models.JSONField()

    def __str__(self):
        return f"Q{self.id}: {self.question[:50]}..."

# class HeroQuestions(models.Model):
#     id = models.AutoField(primary_key=True)
#     topic = models.ForeignKey(Topics, on_delete=models.CASCADE)
#     question = models.ForeignKey(Questions, on_delete=models.CASCADE)
#     stream = models.ForeignKey(Streams, on_delete=models.CASCADE)
#     marks = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
    
class HeroQuestions(models.Model):
    # You might not need the FK from HeroQuestions to Questions if Questions links to Topic
    # but keep it for now as it defines marks/stream context
    id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='hero_instances') # Added related_name
    stream = models.ForeignKey(Streams, on_delete=models.CASCADE)
    marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"HeroQ{self.id} (BaseQ: {self.question_id}, Topic: {self.topic_id}, Marks: {self.marks})"

    
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


# class ResultQuestionLink(models.Model):
#     result_id = models.ForeignKey(TestHistory, on_delete=models.CASCADE)
#     question_id = models.ForeignKey(Questions, on_delete=models.CASCADE)
#     # user_answer = models.TextField() # CHANGE THIS
#     user_answer = models.JSONField() # TO THIS (Requires Django 3.1+ and appropriate DB support)
#     is_correct = models.BooleanField()
    
class ResultQuestionLink(models.Model):
    result_id = models.ForeignKey(TestHistory, on_delete=models.CASCADE, related_name='question_links') # Added related_name
    question_id = models.ForeignKey(Questions, on_delete=models.CASCADE) # Links to base question
    user_answer = models.JSONField()
    is_correct = models.BooleanField()
    # NEW: Store marks specific to this instance in history
    marks_obtained = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=1) # Default=1 is a fallback, should be overwritten

    def __str__(self):
        return f"ResultLink (History: {self.result_id_id}, BaseQ: {self.question_id_id}, Correct: {self.is_correct})"

