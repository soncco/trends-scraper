import unittest
from config import config as settings

from util import get_number_tweets

class TestUtil(unittest.TestCase):
    def test(self):
        self.assertEqual(settings()['places']['Argentina']['tz'], 'UTC-3')

x = TestUtil()
x.test()
