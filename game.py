import pyglet

from math_helper import vec3
from graphics import rotate, translate, identity
from camera import Camera


class Cube:
    def __init__(self, size: int = 10):
        self.position = vec3()
        self.rotation = vec3()
        self.size = vec3(size, size, size)
        self.color = (255, 255, 255)

    def render(self):
        s = self.size
        batch = pyglet.graphics.Batch()
        translate_and_rotate = rotate(self.rotation, translate(self.position, identity()))

        def draw_face(vertices: list, color: iter):
            batch.add(4, pyglet.graphics.GL_QUADS, translate_and_rotate, ('v3f', vertices),
                      ('c3B', (*color, *color, *color, *color)))

        front_vertices = [
            -s.x, s.y, s.z,
            s.x, s.y, s.z,
            s.x, -s.y, s.z,
            -s.x, -s.y, s.z
        ]
        draw_face(front_vertices, (0, 0, 255))

        back_vertices = [
            s.x, s.y, -s.z,
            -s.x, s.y, -s.z,
            -s.x, -s.y, -s.z,
            s.x, -s.y, -s.z
        ]
        draw_face(back_vertices, (0, 255, 0))

        top_vertices = [
            -s.x, s.y, -s.z,
            s.x, s.y, -s.z,
            s.x, s.y, s.z,
            -s.x, s.y, s.z
        ]
        draw_face(top_vertices, (255, 0, 0))

        bottom_vertices = [
            s.x, -s.y, -s.z,
            -s.x, -s.y, -s.z,
            -s.x, -s.y, s.z,
            s.x, -s.y, s.z
        ]
        draw_face(bottom_vertices, (255, 255, 0))

        left_vertices = [
            -s.x, s.y, -s.z,
            -s.x, s.y, s.z,
            -s.x, -s.y, s.z,
            -s.x, -s.y, -s.z
        ]
        draw_face(left_vertices, (255, 0, 255))

        right_vertices = [
            s.x, s.y, s.z,
            s.x, s.y, -s.z,
            s.x, -s.y, -s.z,
            s.x, -s.y, s.z
        ]
        draw_face(right_vertices, (0, 255, 255))

        batch.draw()


class Game:
    def __init__(self):
        self.cube = Cube()
        self.camera = Camera()

    def tick(self, frame_time: float):
        with self.camera.update(frame_time):
            self.cube.render()

    def handle_key_event(self, symbol, modifiers, pressed):
        released = not pressed

        if symbol == pyglet.window.key.ESCAPE and released:
            exit(0)
        elif symbol != pyglet.window.key.ESCAPE:
            print("Key event:", symbol, modifiers, pressed)

        self.camera.handle_key(symbol, pressed)
