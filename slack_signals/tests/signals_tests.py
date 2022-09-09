from unittest.mock import patch
from django.test import TestCase, override_settings
from django.db.models import signals

from slack_signals.models import Todo
from slack_signals.signals import todo_notify_save, todo_notify_delete, slack_channel


class TodoSignalsTestCase(TestCase):
    def setUp(self):
        self.todo = Todo.objects.create(text="text_value")

    def test_notify_save_handler_connected(self):
        post_save_signals = [r[1]() for r in signals.post_save.receivers]
        self.assertIn(todo_notify_save, post_save_signals)

    def test_notify_delete_handler_connected(self):
        post_delete_signals = [r[1]() for r in signals.post_delete.receivers]
        self.assertIn(todo_notify_delete, post_delete_signals)

    @patch('slack_signals.signals.WebClient')
    @override_settings(SLACK_TOKEN='SLACK_TOKEN_VALUE')
    def test_notify_save_on_create(self, MockWebClient):
        mock_web_client = MockWebClient.return_value
        Todo.objects.create(text="text_value")
        MockWebClient.assert_called_once_with(token="SLACK_TOKEN_VALUE")
        mock_web_client.chat_postMessage.assert_called_once_with(channel=slack_channel, text="Todo Created: text_value")

    @patch('slack_signals.signals.WebClient')
    @override_settings(SLACK_TOKEN='SLACK_TOKEN_VALUE')
    def test_notify_save_on_update(self, MockWebClient):
        mock_web_client = MockWebClient.return_value
        self.todo.save()
        MockWebClient.assert_called_once_with(token="SLACK_TOKEN_VALUE")
        mock_web_client.chat_postMessage.assert_called_once_with(channel=slack_channel, text="Todo Updated: text_value")
