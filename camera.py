from pyglet.gl import *

from cube import Cube
from math_helper import vec3, vec2


class Camera:
    def __init__(self):
        self.position = vec3()
        self.direction = vec2(0, 1)
        self.view_angle = vec2()
        self.key_map = {}
        self.mouse_movement = vec2()
        self.sensitivity = 1.0
        self.active = True
        self.model = Cube()

    def set_active(self, active):
        self.active = active

    def update(self, frame_time: float):
        for symbol in self.key_map:
            if not self.key_map[symbol]:
                continue

            speed = 100 * frame_time
            if symbol == pyglet.window.key.W:
                direction = vec3(self.direction.x, 0, self.direction.y)
                self.position += direction * speed
            elif symbol == pyglet.window.key.S:
                direction = vec3(self.direction.x, 0, self.direction.y)
                self.position -= direction * speed

            perpendicular_direction = vec3(self.direction.y, 0, -self.direction.x)
            if symbol == pyglet.window.key.A:
                self.position += perpendicular_direction * speed
            elif symbol == pyglet.window.key.D:
                self.position -= perpendicular_direction * speed

            if symbol == pyglet.window.key.E:
                self.direction.rotate(speed)
                self.view_angle.y += speed
            elif symbol == pyglet.window.key.Q:
                self.direction.rotate(-speed)
                self.view_angle.y -= speed

        if self.mouse_movement.x != 0 or self.mouse_movement.y != 0:
            scale_factor = frame_time * 100 * self.sensitivity
            self.direction.rotate(self.mouse_movement.x * scale_factor)
            self.view_angle.y += self.mouse_movement.x * scale_factor
            self.view_angle.x -= self.mouse_movement.y * scale_factor
            self.mouse_movement = vec2()

        # This is required for the 'with camera.update():' to work
        return self

    def render(self):
        if self.active:
            return

        self.model.rotation = vec3(0, -self.view_angle.y, 0)
        self.model.position = self.position.copy()
        self.model.position.x *= -1
        self.model.position.z *= -1
        self.model.render()

    def __enter__(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glPushMatrix()

        glMatrixMode(GL_PROJECTION)

        glRotatef(self.view_angle.x, 1, 0, 0)
        glRotatef(self.view_angle.y, 0, 1, 0)

        glTranslatef(self.position.x, self.position.y, self.position.z)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glPopMatrix()

    def handle_key(self, symbol, pressed):
        if pressed:
            self.key_map[symbol] = True
        else:
            self.key_map[symbol] = False

    def handle_mouse(self, movement: vec2):
        if movement.x > 0:
            self.mouse_movement.x = 1
        elif movement.x < 0:
            self.mouse_movement.x = -1
        else:
            self.mouse_movement.x = 0

        if movement.y > 0:
            self.mouse_movement.y = 1
        elif movement.y < 0:
            self.mouse_movement.y = -1
        else:
            self.mouse_movement.y = 0
        self.mouse_movement = movement
