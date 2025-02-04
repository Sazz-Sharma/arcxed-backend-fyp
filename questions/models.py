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
    question = models.TextField()


