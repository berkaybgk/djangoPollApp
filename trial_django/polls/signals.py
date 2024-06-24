
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Question

@receiver(post_save, sender=Question)
def my_handler(sender, instance, created, **kwargs):
    if created:
        # Do something when a Question is created
        print(f'New question created: {instance.question_text}')
