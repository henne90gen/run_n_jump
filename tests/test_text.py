import unittest
from text import load_font


class TextTest(unittest.TestCase):
    def test_load_font(self):
        load_font("../font/Roboto-Regular.ttf")
