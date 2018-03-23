import pyglet

from camera import Camera
from cube import Cube
from math_helper import vec2, vec3
from plane import Plane


class Game:
    def __init__(self):
        self.cameras = [Camera()]
        self.camera_index = 0
        position = vec3()
        size = 10
        red = vec3(255, 0, 0)
        green = vec3(0, 255, 0)
        blue = vec3(0, 0, 255)
        self.cubes = [
            Cube(size, position),
            Cube(size, position + vec3(size * 2), red),
            Cube(size, position + vec3(0, size * 2, 0), green),
            Cube(size, position + vec3(0, 0, size * 2), blue),
        ]
        vertices = [
            vec3(-10, -10, -10),
            vec3(-10, -10, 10),
            vec3(10, -20, -10),
            vec3(10, -20, 10),

            vec3(30, -10, -10),
            vec3(30, -10, 10),
        ]
        self.plane = Plane(vertices)

    @property
    def current_camera(self):
        return self.cameras[self.camera_index]

    def next_camera(self):
        self.camera_index += 1
        if self.camera_index >= len(self.cameras):
            self.camera_index = 0

        for camera in self.cameras:
            camera.set_active(False)
        self.current_camera.set_active(True)

    def tick(self, frame_time: float):
        with self.current_camera.update(frame_time):
            for cube in self.cubes:
                cube.render()
            self.plane.render()
            for camera in self.cameras:
                camera.render()

    def handle_key_event(self, symbol, modifiers, pressed):
        released = not pressed

        if symbol == pyglet.window.key.ESCAPE and released:
            exit(0)
        elif symbol != pyglet.window.key.ESCAPE:
            print("Key event:", symbol, modifiers, pressed)

            if symbol == pyglet.window.key.TAB and pressed:
                self.next_camera()
            elif symbol == pyglet.window.key.SPACE and pressed:
                self.cameras.append(Camera())
                self.next_camera()

        self.current_camera.handle_key(symbol, pressed)

    def handle_mouse_motion_event(self, x, y):
        movement = vec2(x, y)
        self.current_camera.handle_mouse(movement)
