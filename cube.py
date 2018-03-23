import pyglet

from graphics import rotate, translate, identity
from math_helper import vec3


class Cube:
    def __init__(self, size: float = 10, position: vec3 = vec3(), color: vec3 = vec3(255, 255, 255)):
        self.position = position
        self.rotation = vec3()
        self.size = vec3(size, size, size)
        self.color = color

    def render(self):
        s = self.size * (1 / 2)
        batch = pyglet.graphics.Batch()
        translate_and_rotate = rotate(self.rotation,
                                      translate(self.position,
                                                identity()))

        def draw_face(vertices: list):
            batch.add(4, pyglet.graphics.GL_QUADS, translate_and_rotate, ('v3f', vertices),
                      ('c3B', (*self.color, *self.color, *self.color, *self.color)))

        front_vertices = [
            -s.x, s.y, s.z,
            s.x, s.y, s.z,
            s.x, -s.y, s.z,
            -s.x, -s.y, s.z
        ]
        draw_face(front_vertices)

        back_vertices = [
            s.x, s.y, -s.z,
            -s.x, s.y, -s.z,
            -s.x, -s.y, -s.z,
            s.x, -s.y, -s.z
        ]
        draw_face(back_vertices)

        top_vertices = [
            -s.x, s.y, -s.z,
            s.x, s.y, -s.z,
            s.x, s.y, s.z,
            -s.x, s.y, s.z
        ]
        draw_face(top_vertices)

        bottom_vertices = [
            s.x, -s.y, -s.z,
            -s.x, -s.y, -s.z,
            -s.x, -s.y, s.z,
            s.x, -s.y, s.z
        ]
        draw_face(bottom_vertices)

        left_vertices = [
            -s.x, s.y, -s.z,
            -s.x, s.y, s.z,
            -s.x, -s.y, s.z,
            -s.x, -s.y, -s.z
        ]
        draw_face(left_vertices)

        right_vertices = [
            s.x, s.y, s.z,
            s.x, s.y, -s.z,
            s.x, -s.y, -s.z,
            s.x, -s.y, s.z
        ]
        draw_face(right_vertices)

        batch.draw()
