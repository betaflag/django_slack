from django import forms
from django.conf import settings
from slack_sdk import WebClient


class SlackButtonForm(forms.Form):
    channel = forms.CharField()
    text = forms.CharField()

    def send_slack_message(self):
        client = WebClient(token=settings.SLACK_TOKEN)
        client.chat_postMessage(channel=self.cleaned_data['channel'], text=self.cleaned_data['text'])
