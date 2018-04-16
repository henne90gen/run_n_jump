import logging

import pyglet

import logging_config
from camera import Camera
from cube import cube
from game_data import GameData
from labyrinth import labyrinth
from math_helper import vec2, vec3
from systems import RenderSystem, PositionSystem, InputSystem, AccelerationSystem, CollisionSystem, ResetSystem
from text import text2d


class Game:
    def __init__(self):
        self.log = logging_config.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        camera_position = vec3(0, 0, -10)
        camera_angle = vec2(0, 0)
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
            # cube(size, vec3(size * 5), red),
            # cube(size, vec3(0, size * 5, 0), green),
            cube(size, vec3(0, 0), blue),
            cube(size, vec3(size * 2 + 1, 0), vec3(255, 0, 255)),
            # labyrinth(),
            text2d("", position=vec2(100, 100), font_size=11),
            text2d(str(vec3(0, 0, size * 5)), position=vec2(100, 80), font_size=11),
        ]

        # del self.camera.player
        # control_index = 2
        # self.entities[control_index].player = True
        # self.entities[control_index].rotation = vec3()
        # self.entities[control_index].speed = 0.005
        # self.entities[control_index].max_speed = 0.05
        # self.entities[control_index].velocity = vec3()
        # self.entities[control_index].acceleration = vec3()

        self.systems = [
            InputSystem(),
            CollisionSystem(),
            AccelerationSystem(),
            PositionSystem(),
            RenderSystem(),
            ResetSystem()
        ]

    def tick(self, game_data: GameData):
        game_data.entities = self.entities
        game_data.view_matrix = self.camera.model_matrix
        game_data.light_position = self.camera.position * -1
        game_data.light_direction = self.light_direction

        for system in self.systems:
            for entity in self.entities:
                if system.supports(entity):
                    self.log.debug(f"Running system {system} on entity {entity}")
                    system.run(game_data, entity)

    def handle_key(self, symbol, modifiers, pressed):
        released = not pressed

        if symbol == pyglet.window.key.ESCAPE and released:
            exit(0)
        elif symbol != pyglet.window.key.ESCAPE:
            self.log.debug("Key event:", symbol, modifiers, pressed)
