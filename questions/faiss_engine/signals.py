from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from questions.models import Questions
from .question_vectorizer import _qv

@receiver(post_save, sender=Questions)
def on_question_save(sender, instance, **kwargs):
    # Ensure index is built before adding
    if not _qv._built:
        _qv.build()
    _qv.add(instance)

@receiver(post_delete, sender=Questions)
def on_question_delete(sender, instance, **kwargs):
    # Rebuild index on deletion
    _qv.rebuild()