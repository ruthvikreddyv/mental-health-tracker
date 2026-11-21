from django.test import SimpleTestCase,override_settings
from django.urls import reverse
from .forms import CheckinForm
from .views import QUESTIONS

class DemoTest(SimpleTestCase):
    @override_settings(PERSISTENT_STORAGE_ENABLED=False)
    def test_public_pages(self):
        for page in ('home','demo','health'):
            self.assertEqual(self.client.get(reverse(page)).status_code,200)
    @override_settings(PERSISTENT_STORAGE_ENABLED=False)
    def test_login_links_to_supabase_auth(self):
        self.assertRedirects(self.client.get(reverse('login')),reverse('demo') + '?auth=login',fetch_redirect_response=False)
        self.assertRedirects(self.client.get(reverse('signup')),reverse('demo') + '?auth=signup',fetch_redirect_response=False)
    def test_checkin_validation(self):
        form=CheckinForm(QUESTIONS,{f'q{i}':'1' for i in range(1,11)})
        self.assertTrue(form.is_valid())
        form=CheckinForm(QUESTIONS,{f'q{i}':'5' for i in range(1,11)})
        self.assertFalse(form.is_valid())
        form=CheckinForm(QUESTIONS,{})
        self.assertFalse(form.is_valid())
