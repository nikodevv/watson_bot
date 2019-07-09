from django.test import TestCase
import json
from unittest import mock


class MiscTests(TestCase):
    def test_admin_url_disabled(self):
        response = self.client.get("admin")
        self.assertEqual(404, response.status_code)

# Facebook requests are mocked
@mock.patch('watson_bot.views.send_message', side_effect=None)
class WebhookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.webhook_endpoint = '/webhook_endpoint/'

    def test_webhook_rejects_empty_post_requests(self, mock_send_msg):
        empty_request_data = json.dumps({"msg": "", "another_field": ''})
        none_request_data = json.dumps({"msg": None})

        response = self.client.post(
            self.webhook_endpoint, 
            data=empty_request_data, content_type="application/json"
            )
        response2 = self.client.post(
            self.webhook_endpoint, 
            data=none_request_data, content_type="application/json"
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response2.status_code, 400)
        mock_send_msg.assert_not_called() # Facebook bot does not get messaged back


    def test_webhook_accepts_non_empty_post(self, mock_send_msg):
        valid_request_data = json.dumps({"msg": "Hi there"})
        mock_send_msg.assert_not_called()

        response = self.client.post(
            self.webhook_endpoint, 
            data=valid_request_data, content_type="application/json"
            )

        self.assertEqual(response.status_code, 200)
        mock_send_msg.assert_called_once()
    