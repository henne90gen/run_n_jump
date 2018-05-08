import unittest

from math_helper import vec3, identity, translate, mat4
from model import BoundingBox
from systems import CollisionSystem


class CollisionTest(unittest.TestCase):
    def test_project(self):
        box = BoundingBox()
        box.vertices = [vec3(2), vec3(-1)]
        normal = vec3(1)
        min_box, max_box = CollisionSystem.project(box, normal)
        self.assertEqual(-1, min_box)
        self.assertEqual(2, max_box)

    normals = [vec3(1), vec3(-1), vec3(0, 1), vec3(0, -1), vec3(0, 0, 1), vec3(0, 0, -1)]
    vertices = [
        vec3(1, 1, 1), vec3(-1, 1, 1),
        vec3(1, -1, 1), vec3(1, 1, -1),
        vec3(1, -1, -1), vec3(-1, 1, -1),
        vec3(-1, -1, 1), vec3(-1, -1, -1)
    ]

    def test_collides_simple(self):
        box = BoundingBox()
        box.vertices = self.vertices
        box.normals = self.normals

        other = BoundingBox()
        other.vertices = self.vertices
        other.normals = self.normals

        matrix = identity()
        collides = CollisionSystem.collides(box, matrix, other, matrix)

        self.assertTrue(collides)

    def test_collides_simple_position(self):
        box = BoundingBox()
        box.vertices = self.vertices
        box.normals = self.normals

        other = BoundingBox()
        other.vertices = self.vertices
        other.normals = self.normals

        matrix = identity()
        translate(matrix, vec3(1))
        collides = CollisionSystem.collides(box, matrix, other, matrix)
        self.assertTrue(collides)

    def test_not_collides_simple_position(self):
        box = BoundingBox()
        box.vertices = self.vertices
        box.normals = self.normals

        other = BoundingBox()
        other.vertices = self.vertices
        other.normals = self.normals

        matrix = identity()
        translate(matrix, vec3(3))
        collides = CollisionSystem.collides(box, matrix, other, identity())
        self.assertFalse(collides)

    def test_collides_example(self):
        vertices = [
            vec3(1.0, -1.0, -1.0), vec3(1.0, -1.0, 1.0),
            vec3(-1.0, -1.0, 1.0), vec3(-1.0, -1.0, -1.0),
            vec3(1.0, 1.0, -0.999999), vec3(0.999999, 1.0, 1.000001),
            vec3(-1.0, 1.0, 1.0), vec3(-1.0, 1.0, -1.0)
        ]
        normals = [
            vec3(1.0, -1.0, -2.0), vec3(2.0, -2.0, 1.0),
            vec3(-2.0, -1.0, 2.0), vec3(-1.0, -2.0, -1.0),
            vec3(2.0, 1.0, -1.0), vec3(1.0, 2.0, 2.0),
            vec3(-1.0, 1.0, 1.0), vec3(-2.0, 2.0, -2.0)
        ]
        box = BoundingBox()
        box.vertices = vertices
        box.normals = normals
        matrix = identity()
        translate(matrix, vec3(0, 0, 25))

        other = BoundingBox()
        other.vertices = vertices
        other.normals = normals
        other_matrix = identity()
        translate(other_matrix, vec3(5, 0, 25))

        collides = CollisionSystem.collides(box, matrix, other, other_matrix)
        self.assertFalse(collides)

    def test_collides_example2(self):
        box = BoundingBox()
        box.vertices = [vec3(1.0, -1.0, -1.0), vec3(1.0, -1.0, 1.0), vec3(-1.0, -1.0, 1.0), vec3(-1.0, -1.0, -1.0),
                        vec3(1.0, 1.0, -0.999999), vec3(0.999999, 1.0, 1.000001), vec3(-1.0, 1.0, 1.0),
                        vec3(-1.0, 1.0, -1.0)]
        box.normals = [vec3(1.0, -1.0, -2.0), vec3(2.0, -2.0, 1.0), vec3(-2.0, -1.0, 2.0), vec3(-1.0, -2.0, -1.0),
                       vec3(2.0, 1.0, -1.0), vec3(1.0, 2.0, 2.0), vec3(-1.0, 1.0, 1.0), vec3(-2.0, 2.0, -2.0)]
        box_model_matrix = mat4()
        box_model_matrix.numbers = [[1.0, 0.0, 0.0, 2.500000000000009], [0.0, 1.0, 0.0, 0.0],
                                    [0.0, 0.0, 1.0, 1.5308084989341933e-16],
                                    [0.0, 0.0, 0.0, 1.0]]

        other = BoundingBox()
        other.vertices = [
            vec3(1.0, -1.0, -1.0), vec3(1.0, -1.0, 1.0), vec3(-1.0, -1.0, 1.0), vec3(-1.0, -1.0, -1.0),
            vec3(1.0, 1.0, -0.999999), vec3(0.999999, 1.0, 1.000001), vec3(-1.0, 1.0, 1.0), vec3(-1.0, 1.0, -1.0)]
        other.normals = [vec3(1.0, -1.0, -2.0), vec3(2.0, -2.0, 1.0), vec3(-2.0, -1.0, 2.0), vec3(-1.0, -2.0, -1.0),
                         vec3(2.0, 1.0, -1.0), vec3(1.0, 2.0, 2.0), vec3(-1.0, 1.0, 1.0), vec3(-2.0, 2.0, -2.0)]
        other_model_matrix = mat4()
        other_model_matrix.numbers = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0],
                                      [0.0, 0.0, 0.0, 1.0]]

        collides = CollisionSystem.collides(box, box_model_matrix, other, other_model_matrix)
        self.assertFalse(collides)
