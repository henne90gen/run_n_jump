import logging

import pyglet

import logging_config
from camera import Camera
from cube import cube
from game_data import GameData
from labyrinth import labyrinth
from math_helper import vec2, vec3
from systems import RenderSystem, PositionSystem, InputSystem, AccelerationSystem, CollisionSystem
from text import text2d


class Game:
    def __init__(self):
        self.log = logging_config.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        camera_position = vec3(-10, 0, -10)
        camera_angle = vec2(0, 180)
        self.camera = Camera(camera_position, camera_angle)

        self.light_position = vec3(50, 0, 50)
        # self.light_position = vec3(0, 20, 0)
        self.light_direction = vec3(0, -1, 0)

        size = 5
        red = vec3(255, 0, 0)
        green = vec3(0, 255, 0)
        blue = vec3(0, 0, 255)
        self.entities = [
            self.camera,
            cube(size, vec3(size * 5), red),
            cube(size, vec3(0, size * 5, 0), green),
            cube(size, vec3(0, 0, size * 5), blue),
            labyrinth(),
            text2d("Hello\n\tWorld", position=vec2(100, 100), font_size=11),
        ]

        self.systems = [
            InputSystem(),
            AccelerationSystem(),
            CollisionSystem(),
            PositionSystem(),
            RenderSystem()
        ]

    def tick(self, game_data: GameData):
        game_data.view_matrix = self.camera.model_matrix
        game_data.light_position = self.camera.position * -1
        game_data.light_direction = self.light_direction

        for entity in self.entities:
            for system in self.systems:
                if system.supports(entity):
                    self.log.debug(f"Running system {system} on entity {entity}")
                    system.run(game_data, entity)

    def handle_key(self, symbol, modifiers, pressed):
        released = not pressed

        if symbol == pyglet.window.key.ESCAPE and released:
            exit(0)
        elif symbol != pyglet.window.key.ESCAPE:
            self.log.debug("Key event:", symbol, modifiers, pressed)
