import unittest

from labyrinth import Labyrinth


class LabyrinthTest(unittest.TestCase):
    def test_init(self):
        lab = Labyrinth("../labyrinth.png")
