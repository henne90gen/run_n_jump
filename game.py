import pyglet

from camera import Camera
from cube import Cube
from math_helper import vec2, vec3, mat4
from model import load_model
from render_data import RenderData
from terrain import Terrain


class Game:
    def __init__(self):
        self.view_matrix = mat4()
        camera_position = vec3(-20, 0, -25)
        camera_angle = vec2(18, 128)
        self.cameras = [Camera(camera_position, camera_angle)]
        self.camera_index = 0

        self.light_position = vec3(50, -10, 50)
        self.light_direction = vec3(0, -1, 0)

        position = vec3()
        size = 10
        red = vec3(255, 0, 0)
        green = vec3(0, 255, 0)
        blue = vec3(0, 0, 255)
        self.cubes = [
            # Cube(size, position, vec3(255, 255, 255)),
            Cube(size, position + vec3(size * 3), red),
            Cube(size, position + vec3(0, size * 3, 0), green),
            Cube(size, position + vec3(0, 0, size * 3), blue),
        ]

        self.terrain = Terrain()
        self.model = load_model("cube.obj")

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

    def tick(self, render_data: RenderData):
        with self.current_camera.update(render_data.frame_time):

            render_data.view_matrix = self.current_camera.view_matrix
            render_data.light_position = self.light_position
            render_data.light_direction = self.light_direction

            for cube in self.cubes:
                cube.render(render_data)

            self.terrain.render(render_data)

            Cube(1, self.light_position).render(render_data)

            self.model.render(render_data)

            for camera in self.cameras:
                camera.render(render_data)

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
        self.terrain.handle_key(symbol, pressed)

    def handle_mouse_motion_event(self, x, y):
        movement = vec2(x, y)
        self.current_camera.handle_mouse(movement)
