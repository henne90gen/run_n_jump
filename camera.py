from pyglet.gl import *

from math_helper import vec3, vec2, identity, rotate, translate


class Camera:
    def __init__(self, position: vec3 = vec3(), angle: vec2 = vec2()):
        # self.view_matrix = identity()
        self.model_matrix = identity()
        self.position = position
        self.rotation = vec3(angle.x, angle.y, 0)

        self.view_angle = angle
        self.direction = vec2(0, 1)
        self.direction.rotate(angle.y)
        self.key_map = {}
        self.mouse_movement = vec2()
        self.sensitivity = 0.5

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

        # self.view_matrix = identity()
        # translate(self.view_matrix, self.position)
        # rotate(self.view_matrix, vec3(self.view_angle.x, self.view_angle.y, 0))

    def input(self, input_map: dict, mouse_movement: vec2):
        self.key_map = input_map

        if mouse_movement.x > 0:
            self.mouse_movement.x = 1
        elif mouse_movement.x < 0:
            self.mouse_movement.x = -1
        else:
            self.mouse_movement.x = 0

        if mouse_movement.y > 0:
            self.mouse_movement.y = 1
        elif mouse_movement.y < 0:
            self.mouse_movement.y = -1
        else:
            self.mouse_movement.y = 0
        self.mouse_movement = mouse_movement
