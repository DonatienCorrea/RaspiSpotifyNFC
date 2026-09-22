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
        }, follow_redirects=True)
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

    def test_missing_spotify_dependency_uses_fake_client(self):
        from app import spotify_service

        original_spotify = spotify_service.Spotify
        original_oauth = spotify_service.SpotifyOAuth
        spotify_service.Spotify = None
        spotify_service.SpotifyOAuth = None

        try:
            client = spotify_service.build_spotify_client()
            self.assertIsInstance(client, spotify_service.FakeSpotifyClient)
            self.assertEqual(spotify_service.dispatch_tag_value('spotify:track:demo')['status'], 'ok')
        finally:
            spotify_service.Spotify = original_spotify
            spotify_service.SpotifyOAuth = original_oauth


if __name__ == '__main__':
    unittest.main()
