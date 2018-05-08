import logging

import pyglet

import logging_config
from camera import Camera
from game_data import GameData
from helper import Timer
from labyrinth import labyrinth, create_labyrinth
from math_helper import vec2, vec3, identity, rotate, translate
from systems import RenderSystem, PositionSystem, InputSystem, MovementInputSystem, AccelerationSystem, \
    BoundingBoxRenderSystem
from text import text2d


class Game:
    def __init__(self):
        self.log = logging_config.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        camera_position = vec3(20, 0, 20)
        camera_angle = vec2(0, 120)
        self.camera = Camera(camera_position, camera_angle)

        self.light_position = vec3(50, 0, 50)
        # self.light_position = vec3(0, 20, 0)
        self.light_direction = vec3(0, -1, 0)

        size = 5
        self.entities = [
            self.camera,
            text2d(str(vec3(0, 0, size * 5)), position=vec2(100, 80), font_size=11),
        ]
        self.labyrinth_generator = labyrinth()
        self.labyrinth_counter = -1

        self.systems = {
            "input": InputSystem(),
            "movement_input": MovementInputSystem(),
            # "collision": CollisionSystem(),
            "acceleration": AccelerationSystem(),
            "position": PositionSystem(),
            "render": RenderSystem(),
            "bbrender": BoundingBoxRenderSystem()
        }

    def tick(self, game_data: GameData):
        game_data.entities = self.entities
        game_data.systems = self.systems

        view_matrix = identity()
        translate(view_matrix, vec3(-self.camera.position.x, self.camera.position.y, -self.camera.position.z))
        rotate(view_matrix, self.camera.rotation)
        game_data.view_matrix = view_matrix

        game_data.light_position = self.camera.position
        game_data.light_direction = self.light_direction

        self.labyrinth_counter += 1
        if self.labyrinth_counter % 20 == 0 and self.labyrinth_generator is not None:
            try:
                lab_params = self.labyrinth_generator.__next__()
                if lab_params is not None:
                    self.entities.append(create_labyrinth(*lab_params))
            except StopIteration:
                self.log.info("Done loading labyrinth")
                self.labyrinth_generator = None

        with Timer(self.log, "MainLoop"):
            for system in self.systems.values():
                with Timer(self.log, system.name):
                    for entity in self.entities:
                        direction = vec2(1).rotate(self.camera.rotation.y - 90)
                        forward_direction = vec3(direction.x, 0, direction.y) * 20

                        if (self.camera.position + forward_direction - entity.position).length > 75:
                            continue

                        if system.supports(entity):
                            self.log.debug(f"Running system {system} on entity {entity}")
                            system.run(game_data, entity)
                    system.reset(game_data)

    def handle_key(self, symbol, modifiers, pressed):
        released = not pressed

        if symbol == pyglet.window.key.ESCAPE and released:
            exit(0)
        elif symbol != pyglet.window.key.ESCAPE:
            self.log.debug("Key event:", symbol, modifiers, pressed)
