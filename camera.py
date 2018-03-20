from math_helper import vec3, vec2
from pyglet.gl import *
import math


class Camera:
    def __init__(self):
        self.position = vec3()
        self.direction = vec3(0, 0, -1)

    def update(self):
        glMatrixMode(GL_PROJECTION)
        glTranslatef(self.position.x, self.position.y, self.position.z)
        angle = math.atan2(self.direction.z, self.direction.x)
        angle = (angle * 180) / math.pi
        glRotatef(angle, 0, 1, 0)

    def handle_key(self, symbol, pressed):
        if symbol == pyglet.window.key.W and pressed:
            self.position.z += 5
        elif symbol == pyglet.window.key.S and pressed:
            self.position.z -= 5

        horizontal_direction = self.direction.to_vec2(['x', 'z'])
        if symbol == pyglet.window.key.E and pressed:
            horizontal_direction.rotate(5)
        elif symbol == pyglet.window.key.Q and pressed:
            horizontal_direction.rotate(-5)
        self.direction.x = horizontal_direction.x
        self.direction.z = horizontal_direction.y
