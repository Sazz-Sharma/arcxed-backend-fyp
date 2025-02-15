from django.db import models

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
    answer = models.TextField()

class HeroQuestions(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer = models.JSONField()
    stream = models.ForeignKey(Streams, on_delete=models.CASCADE)
    marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    



    


