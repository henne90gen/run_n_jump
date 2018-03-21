from math_helper import vec3
from pyglet.gl import *
import math


class Camera:
    def __init__(self):
        self.position = vec3()
        self.direction = vec3(0, 0, 1)
        self.key_map = {}

    def update(self, frame_time: float):
        for symbol in self.key_map:
            if not self.key_map[symbol]:
                continue

            speed = 100 * frame_time
            if symbol == pyglet.window.key.W:
                self.position += self.direction * speed
            elif symbol == pyglet.window.key.S:
                self.position -= self.direction * speed

            if symbol in [pyglet.window.key.A, pyglet.window.key.D]:
                horizontal_direction = self.direction.to_vec2(['z', 'x'])
                perpendicular_direction = vec3(horizontal_direction.x, self.direction.y, -horizontal_direction.y)
                if symbol == pyglet.window.key.A:
                    self.position += perpendicular_direction * speed
                elif symbol == pyglet.window.key.D:
                    self.position -= perpendicular_direction * speed

            if symbol in [pyglet.window.key.E, pyglet.window.key.Q]:
                horizontal_direction = self.direction.to_vec2(['x', 'z'])
                if symbol == pyglet.window.key.E:
                    horizontal_direction.rotate(speed)
                elif symbol == pyglet.window.key.Q:
                    horizontal_direction.rotate(-speed)
                self.direction.x = horizontal_direction.x
                self.direction.z = horizontal_direction.y
                self.direction.normalize()

        # This is required for the 'with camera.update():' to work
        return self

    def __enter__(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glPushMatrix()

        glMatrixMode(GL_PROJECTION)

        angle = math.atan2(self.direction.z, self.direction.x)
        angle = (angle * 180) / math.pi - 90
        glRotatef(angle, 0, 1, 0)

        glTranslatef(self.position.x, self.position.y, self.position.z)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glPopMatrix()

    def handle_key(self, symbol, pressed):
        if pressed:
            self.key_map[symbol] = True
        else:
            self.key_map[symbol] = False
