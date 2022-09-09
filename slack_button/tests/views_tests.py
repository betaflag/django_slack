from unittest import mock
from unittest.mock import patch
from django.contrib.messages import get_messages
from django.test import TestCase
from slack_sdk.errors import SlackApiError

from slack_button.forms import SlackButtonForm


class SlackButtonViewTestCase(TestCase):
    def test_get_success(self):
        response = self.client.get("/slack-button/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('slack_button/slack_button.html', response.template_name)
        self.assertIsInstance(response.context_data["form"], SlackButtonForm)

    @patch('slack_button.views.SlackButtonForm.send_slack_message')
    def test_post_success(self, mock_send_slack_message):
        data = {"channel": "channel_val", "text": "text_val"}
        response = self.client.post("/slack-button/", data)
        self.assertRedirects(response, "/slack-button/", 302, 200)
        mock_send_slack_message.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Message sent successfully")

    @patch('slack_button.views.SlackButtonForm.send_slack_message')
    def test_post_slack_error(self, mock_send_slack_message):
        mock_slack_api_response = mock.MagicMock()
        mock_slack_api_response.__getitem__.return_value = "error_value"
        mock_send_slack_message.side_effect = SlackApiError(message="message", response=mock_slack_api_response)
        data = {"channel": "channel_val", "text": "text_val"}
        response = self.client.post("/slack-button/", data)
        self.assertRedirects(response, "/slack-button/", 302, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'error_value')
