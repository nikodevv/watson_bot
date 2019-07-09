from django.test import TestCase

class WebhookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def test_webhook_rejects_empty_requests(self):
        response = self.client.get('webhook_endpoint')
        self.assertEqual(response.status_code, 400)