import unittest
from math_helper import vec3, vec2


class Vec3Test(unittest.TestCase):
    def test_add(self):
        v1 = vec3(1, 2, 3)
        v2 = vec3(4, 5, 6)
        self.assertEqual(v1 + v2, vec3(5, 7, 9))

    def test_to_vec2(self):
        v = vec3(1, 2, 3)
        self.assertEqual(v.to_vec2({'x': 'y', 'y': 'x'}), vec2(2, 1))
        self.assertEqual(v.to_vec2(['z', 'x']), vec2(3, 1))
        self.assertEqual(v.to_vec2(('x', 'z')), vec2(1, 3))

    def test_spread(self):
        v = vec3(1, 2, 3)
        self.assertEqual([1, 2, 3], [*v])


class Vec2Test(unittest.TestCase):
    def test_add(self):
        v1 = vec2(1, 2)
        v2 = vec2(4, 5)
        self.assertEqual(v1 + v2, vec2(5, 7))

    def test_spread(self):
        v = vec2(1, 2)
        self.assertEqual([1, 2], [*v])

    def test_sub(self):
        v1 = vec2(1, 2)
        v2 = vec2(4, 5)
        self.assertEqual(v1 - v2, vec2(-3, -3))
