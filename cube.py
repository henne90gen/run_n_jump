from ctypes import c_float

import pyglet
from pyglet.gl import *

from math_helper import vec3, identity, rotate, translate
from render_data import RenderData


class Cube:
    def __init__(self, size: float = 10, position: vec3 = vec3(), color: vec3 = vec3(255, 255, 255)):
        self.position = position
        self.rotation = vec3()
        self.size = vec3(size, size, size)
        self.color = color

    def render(self, render_data: RenderData):
        s = self.size * (1 / 2)
        batch = pyglet.graphics.Batch()

        def draw_face(vertices: list):
            batch.add(4, pyglet.graphics.GL_QUADS, None, ('v3f', vertices),
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

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        # noinspection PyCallingNonCallable, PyTypeChecker
        mat = (c_float * 16)(*render_data.projection_matrix.to_list())
        glLoadTransposeMatrixf(mat)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        model_matrix = identity()
        translate(model_matrix, self.position)
        rotate(model_matrix, self.rotation)
        model_view_matrix = render_data.view_matrix * model_matrix

        # noinspection PyCallingNonCallable, PyTypeChecker
        mat = (c_float * 16)(*model_view_matrix.to_list())
        glLoadTransposeMatrixf(mat)

        batch.draw()

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
