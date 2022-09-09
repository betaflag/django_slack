from unittest.mock import patch

from django.test import TestCase, override_settings

from slack_button.forms import SlackButtonForm


class SlackButtonFormTestCase(TestCase):
    def test_is_valid(self):
        form = SlackButtonForm({"channel": "channel_val", "text": "text_val"})
        self.assertTrue(form.is_valid())

    def test_required_fields_errors(self):
        form = SlackButtonForm({})
        self.assertEqual(len(form.errors), 2)
        self.assertIn('This field is required.', form.errors["channel"])
        self.assertIn('This field is required.', form.errors["text"])

    @patch('slack_button.forms.WebClient')
    @override_settings(SLACK_TOKEN='SLACK_TOKEN_VALUE')
    def test_send_slack_message(self, MockWebClient):
        mock_web_client = MockWebClient.return_value
        form = SlackButtonForm({"channel": "channel_val", "text": "text_val"})
        form.is_valid()
        form.send_slack_message()
        MockWebClient.assert_called_once_with(token='SLACK_TOKEN_VALUE')
        mock_web_client.chat_postMessage.assert_called_once_with(channel="channel_val", text="text_val")
