import os
import unittest

from model import load_blender_file


class ModelTest(unittest.TestCase):
    path = "test.obj"

    def setUp(self):
        with open(self.path, "w") as f:
            f.writelines(map(lambda x: x + "\n", [
                "# Blender v2.79 (sub 0) OBJ File: ''",
                "# www.blender.org",
                "o Cube",
                "v 1.000000 -1.000000 -1.000000",
                "v 1.000000 -1.000000 1.000000",
                "v -1.000000 -1.000000 1.000000",
                "v -1.000000 -1.000000 -1.000000",
                "v 1.000000 1.000000 -0.999999",
                "v 0.999999 1.000000 1.000001",
                "v -1.000000 1.000000 1.000000",
                "v -1.000000 1.000000 -1.000000",
                "vn 0.0000 -1.0000 0.0000",
                "vn 0.0000 1.0000 0.0000",
                "vn 1.0000 -0.0000 0.0000",
                "vn 0.0000 -0.0000 1.0000",
                "vn -1.0000 -0.0000 -0.0000",
                "vn 0.0000 0.0000 -1.0000",
                "s off",
                "f 2//1 4//1 1//1",
                "f 8//2 6//2 5//2",
                "f 5//3 2//3 1//3",
                "f 6//4 3//4 2//4",
                "f 3//5 8//5 4//5",
                "f 1//6 8//6 5//6",
                "f 2//1 3//1 4//1",
                "f 8//2 7//2 6//2",
                "f 5//3 6//3 2//3",
                "f 6//4 7//4 3//4",
                "f 3//5 7//5 8//5",
                "f 1//6 4//6 8//6"
            ]))

    def tearDown(self):
        os.remove(self.path)

    def test_load_model(self):
        model = load_blender_file(self.path)
        self.assertIsNotNone(model)
