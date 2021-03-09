import unittest

from web_app.stages import baseline


class DataTest(unittest.TestCase):
    def test_function(self):
        self.assertEqual("foo".upper(), "foo")
