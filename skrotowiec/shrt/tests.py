import unittest

from django.test import TestCase
from rest_framework.test import APIClient

from skrotowiec.shrt import models

TEST_URL = 'http://example.com/very-very/long/url/even-longer'


class GeneratorTestCase(unittest.TestCase):
    def test_short_pk(self) -> None:
        """Basic use case"""
        result: str = models.generate_short_pk(length=3)
        self.assertEqual(len(result), 3)


class GeneratorDBTestCase(TestCase):
    def test_unique_pk(self) -> None:
        """Basic use case"""
        models.generate_unique_pk()

    def test_unique_pk_with_filled_db(self) -> None:
        """Tests when single character pool is already used up"""
        for c in models.ALLOWED_CHARACTERS:
            _ = models.ShortenedURL.objects.create(short=c, full=TEST_URL)
        result: str = models.generate_unique_pk(max_length=3)
        self.assertEqual(len(result), 2)


class HappyPathE2ETestCase(TestCase):
    def test_simple_case(self) -> None:
        """"Tests happy path functionality"""
        client = APIClient()
        response = client.post('/shrt/', {'full':TEST_URL,})
        self.assertEqual(response.status_code, 201)
        reversed_response = client.get(response.json()['url'])
        self.assertEqual(reversed_response.status_code, 200)
        self.assertEqual(reversed_response.json()['full'], TEST_URL)
