import pyglet

from camera import Camera
from cube import Cube
from labyrinth import Labyrinth
from math_helper import vec2, vec3, mat4
from model import load_model
from render_data import RenderData
from terrain import Terrain
from text import Text2D


class Game:
    def __init__(self):
        self.view_matrix = mat4()
        camera_position = vec3(-10, 0, -10)
        camera_angle = vec2(0, 120)
        self.camera = Camera(camera_position, camera_angle)

        self.light_position = vec3(50, 0, 50)
        # self.light_position = vec3(0, 20, 0)
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
        self.model = load_model("models/model.obj")
        self.model.scale = 5.0
        self.text = Text2D("Hello\n\tWorld", vec2(100, 100), vec3(1.0), font_size=48)

        self.labyrinth = Labyrinth()

    def tick(self, render_data: RenderData):
        self.camera.update(render_data.frame_time)

        render_data.view_matrix = self.camera.view_matrix
        render_data.light_position = self.camera.position * -1
        render_data.light_direction = self.light_direction

        for cube in self.cubes:
            cube.render(render_data)

        self.labyrinth.render(render_data)

        self.text.render(render_data)

    def handle_key_event(self, symbol, modifiers, pressed):
        released = not pressed

        if symbol == pyglet.window.key.ESCAPE and released:
            exit(0)
        elif symbol != pyglet.window.key.ESCAPE:
            print("Key event:", symbol, modifiers, pressed)

        self.camera.handle_key(symbol, pressed)
        self.terrain.handle_key(symbol, pressed)

    def handle_mouse_motion_event(self, x, y):
        movement = vec2(x, y)
        self.camera.handle_mouse(movement)
