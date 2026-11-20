"""Tests that do not need a running PostgreSQL database."""
from unittest.mock import Mock, patch
from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse
from . import cloud_api

class CloudApiTest(SimpleTestCase):
    def setUp(self):
        self.factory=RequestFactory()

    @patch('detector.cloud_api.configured',return_value=False)
    def test_config_is_safe_when_disabled(self, _):
        response=cloud_api.api_config(self.factory.get('/api/config/'))
        self.assertContains(response, 'false')

    @patch('detector.cloud_api.configured',return_value=False)
    def test_write_requires_configured_backend(self, _):
        request=self.factory.post('/api/journals/', data='{"text":"Hello"}',content_type='application/json')
        response=cloud_api.journals(request)
        self.assertEqual(response.status_code,503)

    @patch('detector.cloud_api.identity', return_value=(('00000000-0000-0000-0000-000000000001', {}), None))
    @patch('detector.cloud_api.proxy')
    def test_server_rejects_invalid_checkin_scores(self, fake_proxy, _):
        request=self.factory.post('/api/checkins/',data='{"answers":[0,0,0,0,0,0,0,0,0,99]}',content_type='application/json')
        response=cloud_api.checkins(request)
        self.assertEqual(response.status_code,400)
        fake_proxy.assert_not_called()

    @patch('detector.cloud_api.identity', return_value=(('00000000-0000-0000-0000-000000000001', {}), None))
    @patch('detector.cloud_api.proxy')
    def test_score_is_calculated_server_side(self, fake_proxy, _):
        fake_proxy.return_value=Mock(status_code=201)
        request=self.factory.post('/api/checkins/',data='{"answers":[1,1,1,1,1,1,1,1,1,1],"total":30}',content_type='application/json')
        cloud_api.checkins(request)
        self.assertEqual(fake_proxy.call_args.kwargs['payload']['total'],10)

    @patch('detector.cloud_api.identity', return_value=(('00000000-0000-0000-0000-000000000001', {}), None))
    @patch('detector.cloud_api.proxy')
    def test_journal_too_long_is_rejected(self, fake_proxy, _):
        request=self.factory.post('/api/journals/',data='{"text":"'+('x'*3001)+'"}',content_type='application/json')
        response=cloud_api.journals(request)
        self.assertEqual(response.status_code,400)
        fake_proxy.assert_not_called()
