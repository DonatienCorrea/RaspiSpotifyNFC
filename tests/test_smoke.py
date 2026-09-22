import unittest

from app.db import clear_all_tags
from app.web import create_app


class SmokeTests(unittest.TestCase):
    def setUp(self):
        clear_all_tags()
        self.app = create_app()
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')

    def test_assign_and_dispatch_playlist(self):
        assign = self.client.post('/assign', data={
            'uid': 'UID-001',
            'value': 'spotify:playlist:123abc',
            'label': 'Morning mix'
        })
        self.assertEqual(assign.status_code, 200)

        dispatch = self.client.post('/dispatch', data={'uid': 'UID-001'})
        self.assertEqual(dispatch.status_code, 200)
        payload = dispatch.get_json()
        self.assertEqual(payload['status'], 'ok')
        self.assertIn('mode', payload['result'])

    def test_play_pause_action(self):
        dispatch = self.client.post('/dispatch', data={'value': 'action:play_pause'})
        self.assertEqual(dispatch.status_code, 200)
        payload = dispatch.get_json()['result']
        self.assertEqual(payload['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
