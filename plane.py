import pyglet

from graphics import rotate, translate, identity
from math_helper import vec3, vec2


class Plane:
    def __init__(self, vertices: list):
        self.position = vec3()
        self.rotation = vec3()
        self.vertices = vertices
        self.color = vec3(255, 255, 255)

    def render(self):
        batch = pyglet.graphics.Batch()
        translate_and_rotate = rotate(self.rotation,
                                      translate(self.position,
                                                identity()))

        vertices = []
        for v in self.vertices:
            vertices.append(v.x)
            vertices.append(v.y)
            vertices.append(v.z)

        color = []
        for v in self.vertices:
            color.append(self.color.x)
            color.append(self.color.y)
            color.append(self.color.z)
        batch.add(len(self.vertices), pyglet.graphics.GL_TRIANGLE_STRIP, translate_and_rotate, ('v3f', vertices), ('c3B', color))

        batch.draw()
