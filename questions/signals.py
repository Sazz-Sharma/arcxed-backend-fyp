# your_app_name/signals.py (create this file if it doesn't exist)
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import HeroQuestions, Questions

@receiver(post_delete, sender=HeroQuestions)
def delete_orphaned_question(sender, instance, **kwargs):
    """
    After a HeroQuestions instance is deleted, check if its related
    Question instance is now orphaned. If so, delete it.
    """
    question_to_check = instance.question # The Question instance before HeroQuestion was deleted

    if question_to_check:
        # Check if any other HeroQuestions still refer to this Question
        # The 'instance' (HeroQuestion) is already deleted from the DB at this point,
        # so hero_instances query will reflect that.
        if not question_to_check.hero_instances.exists():
            question_to_check.delete()

# your_app_name/apps.py
from django.apps import AppConfig

class QuestionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app_name'

    def ready(self):
        import questions.signals # Import signals here

# Make sure YourAppNameConfig is registered in settings.INSTALLED_APPS