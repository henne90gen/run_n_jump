import unittest

import numpy as np

from labyrinth import generate_vertices_efficient


class LabyrinthTest(unittest.TestCase):
    def test_generate_vertices_efficient(self):
        width, height = 5, 5
        arr = np.zeros((width, height))
        arr[0, 0] = 255
        arr[1, 0] = 255
        arr[2, 0] = 255
        arr[3, 0] = 255
        arr[4, 0] = 255
        arr[0, 1] = 255
        arr[1, 1] = 255
        arr[2, 1] = 255
        arr[3, 1] = 255
        arr[4, 1] = 255
        for row in range(arr.shape[1]):
            print(arr[row])
        generate_vertices_efficient(arr)
