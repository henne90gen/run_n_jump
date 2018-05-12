import logging

import pyglet

import logging_config
from camera import Camera
from debug_ui import create_debug_ui
from game_data import GameData
from helper import Timer
from labyrinth import labyrinth, create_labyrinth
from math_helper import vec2, vec3, identity, rotate, translate
from quad_tree import QuadTree, build_quad_tree
from systems import RenderSystem, PositionSystem, InputSystem, MovementInputSystem, AccelerationSystem, \
    BoundingBoxRenderSystem, GlobalInputSystem, DebugUISystem, CollisionSystem


class Game:
    def __init__(self):
        self.log = logging_config.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        camera_position = vec3(20, 0, 20)
        camera_angle = vec2(0, 120)
        self.camera = Camera(camera_position, camera_angle)

        self.frame_counter = -1

        self.light_position = vec3(50, 0, 50)
        self.light_direction = vec3(0, -1, 0)

        self.entities = [
            self.camera,
        ]

        self.labyrinth_generator = labyrinth()

        self.systems = {
            "input": InputSystem(),
            "movement_input": MovementInputSystem(),
            "collision": CollisionSystem(),
            "acceleration": AccelerationSystem(),
            "position": PositionSystem(),
            "render": RenderSystem(),
            "bbrender": BoundingBoxRenderSystem(),
            "debug_ui": DebugUISystem(),
            "global_input": GlobalInputSystem()
        }

        self.ui_elements = [
            *create_debug_ui(map(lambda s: s.name, self.systems.values())),
        ]

    def tick(self, game_data: GameData):
        self.frame_counter += 1
        self.finish_loading_labyrinth()

        game_data.entities = build_quad_tree(self.entities)
        game_data.systems = self.systems
        game_data.camera = self.camera
        if not game_data.show_overview:
            game_data.player_configuration = (self.camera.position, self.camera.rotation)

        view_matrix = identity()
        translate(view_matrix, self.camera.position * -1)
        rotate(view_matrix, self.camera.rotation)
        game_data.view_matrix = view_matrix

        game_data.light_position = self.camera.position
        game_data.light_direction = self.light_direction

        self.run_systems(game_data)

        for index, element in enumerate(self.ui_elements):
            if self.frame_counter % len(self.ui_elements) - index == 0:
                self.systems['debug_ui'].run(game_data, element)
            self.systems['position'].run(game_data, element)
            self.systems['render'].run(game_data, element)

    def finish_loading_labyrinth(self):
        if self.frame_counter % 20 == 0 and self.labyrinth_generator is not None:
            try:
                lab_params = self.labyrinth_generator.__next__()
                if lab_params is not None:
                    self.entities.append(create_labyrinth(*lab_params))
            except StopIteration:
                self.log.info("Done loading labyrinth")
                self.labyrinth_generator = None

    def run_systems(self, game_data):
        self.systems['global_input'].run(game_data, None)

        with Timer(self.log, "MainLoop") as main_timer:
            query_positions = self.get_query_positions(game_data)
            entities = []
            for position in query_positions:
                entities.extend(game_data.entities.query(position))

            self.log.debug(f"{len(entities)} entities")
            for entity in entities:
                for system_name in entity.systems:
                    if system_name not in self.systems:
                        continue

                    system = self.systems[system_name]
                    if system.supports(entity):
                        self.log.debug(f"Running system {system} on entity {entity}")
                        system.run(game_data, entity)

            for system in self.systems.values():
                system.reset(game_data)

        game_data.debug_data["total_time"] = main_timer.time_diff

    def get_query_positions(self, game_data: GameData):
        if not game_data.show_overview:
            return [self.camera.position]

        position = vec2(
            game_data.mouse_position.x,
            game_data.screen_dimensions.y - game_data.mouse_position.y
        )
        position -= game_data.screen_dimensions / 2
        position += vec2(250, 250)

        position = vec3(position.x, 0, position.y)
        return position, game_data.player_configuration[0]

    def handle_key(self, symbol, modifiers, pressed):
        released = not pressed

        if symbol == pyglet.window.key.ESCAPE and released:
            exit(0)
        elif symbol != pyglet.window.key.ESCAPE:
            self.log.debug("Key event:", symbol, modifiers, pressed)
