from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from slack_sdk.errors import SlackApiError

from slack_button.forms import SlackButtonForm


class SlackButtonView(FormView):
    template_name = "slack_button/slack_button.html"
    form_class = SlackButtonForm
    success_url = reverse_lazy("slack-button")

    def form_valid(self, form):
        try:
            form.send_slack_message()
            messages.success(self.request, "Message sent successfully")
        except SlackApiError as e:
            messages.error(self.request, e.response["error"])
        return super().form_valid(form)
