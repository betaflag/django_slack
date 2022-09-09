from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings

from slack_webhook.views import webhook_view


class WebhookViewTestCase(TestCase):
    @patch('slack_webhook.views.SignatureVerifier')
    def test_forbidden(self, MockVerifier):
        mock_verifier = MockVerifier.return_value
        mock_verifier.is_valid_request.return_value = False
        response = self.client.post('/slack-webhook/')
        MockVerifier.assert_called_once()
        self.assertEqual(response.status_code, 403)

    @patch('slack_webhook.views.SignatureVerifier')
    @override_settings(SLACK_SIGNING_SECRET='SLACK_SIGNING_SECRET_VALUE')
    def test_success(self, MockVerifier):
        mock_verifier = MockVerifier.return_value
        mock_verifier.is_valid_request.return_value = True
        data = "test data"
        request = RequestFactory().post('/slack-webhook/', data, content_type='application/json')
        response = webhook_view(request)
        MockVerifier.assert_called_once_with(signing_secret='SLACK_SIGNING_SECRET_VALUE')
        mock_verifier.is_valid_request.assert_called_once_with(request.body.decode("utf-8"), request.headers)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"text": "Hello from Django!"})
