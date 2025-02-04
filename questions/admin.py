from django.contrib import admin

# Register your models here.
from .models import Subjects, Streams, Chapters

admin.site.register(Subjects)
admin.site.register(Streams)
admin.site.register(Chapters)