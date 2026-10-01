from unittest.mock import patch
from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase, override_settings
from dashboard.routing import websocket_urlpatterns

class DashboardTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user('admin', is_staff=True)
        self.user = get_user_model().objects.create_user('user')
    def test_access_restricted(self):
        for url in ['/dashboard/', '/dashboard/jobs/', '/dashboard/utilisateurs/', '/dashboard/stats/']:
            self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/dashboard/').status_code, 302)
    @patch('dashboard.presence.count_connected', return_value=2)
    def test_staff_pages_without_p2(self, presence):
        self.client.force_login(self.staff)
        for url in ['/dashboard/', '/dashboard/jobs/', '/dashboard/utilisateurs/']:
            self.assertEqual(self.client.get(url).status_code, 200)
        result = self.client.get('/dashboard/stats/').json()
        self.assertFalse(result['p2_disponible'])
        self.assertEqual(result['utilisateurs'], 2)
        self.assertEqual(result['utilisateurs_connectes'], 2)
        self.assertEqual(self.client.get('/').status_code, 404)
    def test_toggle_requires_post_and_protects_admin(self):
        self.client.force_login(self.staff)
        url = f'/dashboard/utilisateurs/{self.user.pk}/activer/'
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.client.post(url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.client.post(f'/dashboard/utilisateurs/{self.staff.pk}/activer/')
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_active)
    def test_job_actions_wait_for_p2(self):
        self.client.force_login(self.staff)
        for action in ['relancer', 'supprimer']:
            self.assertEqual(self.client.post(f'/dashboard/jobs/00000000-0000-0000-0000-000000000001/{action}/').status_code, 503)

@override_settings(CHANNEL_LAYERS={'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}})
class AdminSocketTests(TransactionTestCase):
    @patch('dashboard.presence.count_connected', return_value=0)
    def test_staff_only_and_stats(self, presence):
        staff = get_user_model().objects.create_user('admin', is_staff=True)
        user = get_user_model().objects.create_user('user')
        async def check():
            for account, allowed in [(user, False), (staff, True)]:
                connection = WebsocketCommunicator(URLRouter(websocket_urlpatterns), '/ws/admin/')
                connection.scope['user'] = account
                connected, _ = await connection.connect()
                self.assertEqual(connected, allowed)
                if allowed:
                    result = await connection.receive_json_from()
                    self.assertEqual(result['type'], 'admin.stats')
                await connection.disconnect()
        async_to_sync(check)()
