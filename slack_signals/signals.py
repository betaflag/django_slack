from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from slack_sdk import WebClient

from slack_signals.models import Todo

slack_channel = "general"


@receiver(post_save, sender=Todo)
def todo_notify_save(instance, created, **_kwargs):
    action = "Created" if created else "Updated"
    text = f"Todo {action}: {instance}"
    client = WebClient(token=settings.SLACK_TOKEN)
    client.chat_postMessage(channel=slack_channel, text=text)


@receiver(post_delete, sender=Todo)
def todo_notify_delete(instance, **_kwargs):
    text = f"Todo Deleted: {instance}"
    client = WebClient(token=settings.SLACK_TOKEN)
    client.chat_postMessage(channel=slack_channel, text=text)
