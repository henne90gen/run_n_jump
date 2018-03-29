import unittest
from math_helper import vec3, vec2
import math_helper
from PIL import Image


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


class PerlinTest(unittest.TestCase):
    def test_gradient(self):
        pixels = []
        size = vec2(1000, 1000)
        for y in range(size.y):
            for x in range(size.x):
                noise = math_helper.perlin(x / 100, y / 100)
                noise += 1
                noise /= 2
                noise *= 255
                pixels.append(noise)

        img = Image.new('L', (size.x, size.y))
        img.putdata(pixels)
        with open('perlin_noise.png', 'wb') as f:
            img.save(f)
