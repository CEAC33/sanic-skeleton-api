import unittest
from http import HTTPStatus
from tests import build_full_app
from main import version, 

class SampleApiTest(unittest.TestCase):
    def setUp(self):
        self.app = build_full_app()
        self.headers = {'Accept': 'application/vnd.api+json'}

    def test_return_pong(self):
        request, response = self.app.test_client.get('/', headers=self.headers)
        self.assertEqual(HTTPStatus.OK, response.status)
        self.assertEqual('This is a test text', response.text)

if __name__ == '__main__':
    unittest.main()
