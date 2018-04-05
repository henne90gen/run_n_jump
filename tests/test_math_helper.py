import unittest

from PIL import Image

import math_helper
from math_helper import vec3, vec2, cross, mat4, identity, translate, rotate


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


class MethodTest(unittest.TestCase):
    def test_cross_product(self):
        v1 = vec3()
        v2 = vec3()
        self.assertEqual(vec3(), cross(v1, v2))

        v1 = vec3(1, 0, 0)
        v2 = vec3(0, 1, 0)
        self.assertEqual(vec3(0, 0, 1), cross(v1, v2))

    def test_translate(self):
        m = identity()
        v = vec3(1, 2, 3)
        translate(m, v)
        self.assertEqual(mat4([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ]), m)

    def test_rotate_around_x(self):
        m = identity()
        v1 = vec3(90)
        rotate(m, v1)
        self.assertEqual(mat4([
            [1, 0, 0, 0],
            [0, 0, -1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ]), m)
        v2 = m * vec3(0, 1, 0)
        self.assertEqual(vec3(0, 0, 1), v2)

    def test_rotate_around_y(self):
        m = identity()
        v1 = vec3(0, 90)
        rotate(m, v1)
        self.assertEqual(mat4([
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [-1, 0, 0, 0],
            [0, 0, 0, 1]
        ]), m)
        v2 = m * vec3(1, 0, 0)
        self.assertEqual(vec3(0, 0, -1), v2)

    def test_rotate_around_x_and_y(self):
        m = identity()
        v1 = vec3(90, 90)
        rotate(m, v1)
        self.assertEqual(mat4([
            [0, 1, 0, 0],
            [0, 0, -1, 0],
            [-1, 0, 0, 0],
            [0, 0, 0, 1]
        ]), m)
        v2 = m * vec3(0, 1, 0)
        self.assertEqual(vec3(1, 0, 0), v2)

    def test_rotate_and_translate(self):
        m = identity()
        rot = vec3(90)
        trans = vec3(1, 2, 3)
        rotate(m, rot)
        translate(m, trans)
        self.assertEqual(mat4([
            [1.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0, 2.0],
            [0.0, 1.0, 0.0, 3.0],
            [0.0, 0.0, 0.0, 1.0]
        ]), m)
        v = m * vec3(0, 1, 0)
        self.assertEqual(vec3(1, 2, 4), v)


class Mat4Test(unittest.TestCase):
    def test_init(self):
        m = mat4()
        self.assertEqual([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], m.numbers)
        m = mat4([[1, 2, 3, 4]])
        self.assertEqual([[1, 2, 3, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], m.numbers)

    def test_mul_identity(self):
        m1 = identity()
        m2 = identity()
        self.assertEqual(identity(), m1 * m2)
        self.assertEqual(identity(), m1)
        self.assertEqual(identity(), m2)

    def test_mul_mat4(self):
        m1 = mat4([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ])
        m2 = mat4([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ])
        self.assertEqual(mat4([
            [1, 0, 0, 2],
            [0, 1, 0, 4],
            [0, 0, 1, 6],
            [0, 0, 0, 1]
        ]), m1 * m2)
        self.assertEqual(mat4([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ]), m1)
        self.assertEqual(mat4([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ]), m2)

    def test_mul_vec3(self):
        m = mat4([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ])
        v = vec3(2, 3, 4)
        self.assertEqual(vec3(3, 5, 7), m * v)
        self.assertEqual(mat4([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ]), m)
        self.assertEqual(vec3(2, 3, 4), v)

    def test_to_list(self):
        m = mat4([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ])
        self.assertEqual([1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 2.0, 0.0, 0.0, 1.0, 3.0, 0.0, 0.0, 0.0, 1.0], m.to_list())
        self.assertEqual([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 2.0, 3.0, 1.0],
                         m.to_list(True))


@unittest.skip
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
