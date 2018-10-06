import logging

from pyglet.gl import *

import run_n_jump.logging_config as logging_config
from .game_data import GameData
from .math_helper import identity, translate, vec3, rotate, vec2, scale, dot, mat4
from .model import BoundingBox
from .text import update_text


class System:
    def __init__(self, name, components: list = None, optional_components: list = None):
        if components is None:
            components = []
        if optional_components is None:
            optional_components = []
        self.components = components
        self.optional_components = optional_components
        self.name = name

        self.log = logging_config.getLogger(self.name)
        self.log.setLevel(logging.INFO)

    def supports(self, entity):
        for component in self.components:
            if not hasattr(entity, component):
                return False
        return True

    def reset(self, game_data: GameData):
        pass

    def run(self, game_data: GameData, entity):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


class GlobalInputSystem(System):
    def __init__(self):
        super().__init__("GlobalInput")

    def run(self, game_data: GameData, entity):
        if pyglet.window.key.SPACE in game_data.key_map and game_data.key_map[pyglet.window.key.SPACE]:
            game_data.wireframe = not game_data.wireframe
            del game_data.key_map[pyglet.window.key.SPACE]
            self.log.info(f"Switched to wireframe={game_data.wireframe}")

        if pyglet.window.key.O in game_data.key_map and game_data.key_map[pyglet.window.key.O]:
            game_data.show_overview = not game_data.show_overview
            del game_data.key_map[pyglet.window.key.O]
            if game_data.show_overview:
                game_data.camera.position = vec3(250, 100, 250)
                game_data.camera.rotation = vec3(90, 0, 0)
                game_data.camera.player = False
            else:
                game_data.camera.position = game_data.player_configuration[0]
                game_data.camera.rotation = game_data.player_configuration[1]
                game_data.camera.player = True
            self.log.info(f"Switched to show_overview={game_data.show_overview}")

    def reset(self, game_data: GameData):
        pass


class DebugUISystem(System):
    def __init__(self):
        super().__init__("DebugUI")

    def run(self, game_data: GameData, entity):
        if hasattr(entity, "text"):
            try:
                new_text = entity.text.format(**game_data.debug_data)
                update_text(entity, new_text)
            except KeyError as e:
                self.log.error(f"Missing debug data: {e}")


class InputSystem(System):
    def __init__(self):
        super().__init__("Input", ['asset'], [
            'current_index_buffer_id', 'index_buffers'])

    def run(self, game_data: GameData, entity):
        pass

    def reset(self, game_data: GameData):
        pass


class MovementInputSystem(System):
    def __init__(self):
        super().__init__("MovementInput", [
            'player', 'acceleration', 'rotation', 'velocity'], ['speed'])

    def run(self, game_data: GameData, entity):
        if game_data.show_overview:
            return

        if game_data.mouse_movement.x != 0 or game_data.mouse_movement.y != 0:
            scale_factor = game_data.frame_time * 100 * game_data.sensitivity
            entity.rotation.x -= game_data.mouse_movement.y * scale_factor
            entity.rotation.y += game_data.mouse_movement.x * scale_factor

        direction = vec2(1).rotate(entity.rotation.y + 90)
        sideways_direction = vec3(-direction.y, 0, direction.x)
        forward_direction = vec3(direction.x, 0, direction.y)

        movement = vec2()
        for symbol in game_data.key_map:
            if not game_data.key_map[symbol]:
                continue
            if symbol in [pyglet.window.key.W, pyglet.window.key.S]:
                if symbol == pyglet.window.key.W and movement.y != -1:
                    movement.y = -1
                elif symbol == pyglet.window.key.S and movement.y != 1:
                    movement.y = 1
                else:
                    movement.y = 0

            if symbol in [pyglet.window.key.D, pyglet.window.key.A]:
                if symbol == pyglet.window.key.D and movement.x != -1:
                    movement.x = -1
                elif symbol == pyglet.window.key.A and movement.x != 1:
                    movement.x = 1
                else:
                    movement.x = 0

        if movement == vec2():
            entity.acceleration = vec3()
            entity.velocity = vec3()
            return

        forward_direction *= movement.y
        sideways_direction *= movement.x
        final_direction = forward_direction + sideways_direction
        entity.acceleration = final_direction * game_data.frame_time
        if hasattr(entity, 'speed'):
            entity.acceleration *= entity.speed

        if entity.velocity == vec3():
            entity.velocity = final_direction.copy().normalize()


class AccelerationSystem(System):
    def __init__(self):
        super().__init__("Acceleration", [
            'velocity', 'acceleration'], ['speed', 'max_speed'])

    def run(self, game_data: GameData, entity):
        if entity.velocity.length > 0:
            drag = entity.velocity.copy().normalize() * -0.5 * game_data.frame_time
        else:
            drag = vec3()

        if hasattr(entity, 'speed'):
            drag *= entity.speed

        entity.velocity += entity.acceleration + drag
        if hasattr(entity, 'max_speed'):
            if entity.velocity.length > entity.max_speed:
                entity.velocity = entity.velocity.normalize() * entity.max_speed
        entity.acceleration = vec3()


class CollisionSystem(System):
    def __init__(self):
        super().__init__("Collision", ['model_matrix', 'bounding_boxes'])
        self.loop_counter = 0
        self.collision_counter = 0

    @staticmethod
    def project(box: BoundingBox, normal: vec3):
        min_box = None
        max_box = None
        for vertex in box.vertices:
            projection = dot(box.model_matrix * vertex, normal)
            if min_box is None or min_box > projection:
                min_box = projection
            if max_box is None or max_box < projection:
                max_box = projection
        return float(min_box), float(max_box)

    @staticmethod
    def get_overlap(start1, end1, start2, end2):
        if start1 <= start2 <= end2 <= end1:
            return abs(end2 - start2)
        elif start2 <= start1 <= end1 <= end2:
            return abs(end1 - start1)
        elif start1 <= start2:
            return abs(end1 - start2)
        elif start2 <= start1:
            return abs(end2 - start1)
        return 0

    @staticmethod
    def check_for_overlap(normals: list, rotation_matrix: mat4, box: BoundingBox, other: BoundingBox):
        minimum_overlap = None
        overlap_normal = None
        for normal in normals:
            normal = (rotation_matrix * normal.copy()).normalize()
            min_box, max_box = CollisionSystem.project(box, normal)
            min_other, max_other = CollisionSystem.project(other, normal)
            if max_box < min_other and max_box < max_other:
                return None, None
            elif min_box > min_other and min_box > max_other:
                return None, None
            else:
                overlap = CollisionSystem.get_overlap(
                    min_box, max_box, min_other, max_other)
                if minimum_overlap is None or minimum_overlap > overlap:
                    minimum_overlap = overlap
                    overlap_normal = normal

        return minimum_overlap, overlap_normal

    @staticmethod
    def collides(box: BoundingBox, box_rotation_matrix: mat4, other: BoundingBox, other_rotation_matrix: mat4):
        minimum_overlap, overlap_normal = CollisionSystem.check_for_overlap(box.normals, box_rotation_matrix, box,
                                                                            other)
        if minimum_overlap is None or overlap_normal is None:
            return False, None

        minimum_overlap, overlap_normal = CollisionSystem.check_for_overlap(other.normals, other_rotation_matrix, box,
                                                                            other)
        if minimum_overlap is None or overlap_normal is None:
            return False, None

        return True, overlap_normal * (minimum_overlap + 0.000000000000001)

    @staticmethod
    def no_collision_possible(entity, other, box, other_box):
        if box.type == 'static':
            return True

        if hasattr(box, 'radius') and hasattr(other_box, 'radius'):
            box_pos = box.model_matrix * vec3()
            other_pos = other_box.model_matrix * vec3()
            diff = box_pos - other_pos
            if diff.length > box.radius * entity.scale + other_box.radius * other.scale:
                return True
        return False

    def do_collision_check(self, entity, other, box, other_box):
        entity_rotation_matrix = identity()
        if hasattr(entity, 'rotation'):
            rotate(entity_rotation_matrix, entity.rotation)
        other_rotation_matrix = identity()
        if hasattr(other, 'rotation'):
            rotate(other_rotation_matrix, other.rotation)

        collides, overlap = self.collides(
            box, entity_rotation_matrix,
            other_box, other_rotation_matrix
        )
        self.collision_counter += 1
        if collides:
            dot_entity = dot(box.model_matrix * vec3(), overlap)
            dot_other = dot(other_box.model_matrix * vec3(), overlap)
            direction = dot_entity - dot_other
            if direction < 0:
                direction = -1
            elif direction > 0:
                direction = 1
            else:
                direction = 0
            overlap *= direction

            self.log.debug(
                f"{entity} collides with {other} with an overlap of {overlap}")

            entity.collision = overlap
            other.collision = overlap * -1

    def run(self, game_data: GameData, entity):
        for other in game_data.entities.query(entity.position):
            if entity == other or not (hasattr(other, 'model_matrix') and hasattr(other, 'bounding_boxes')):
                continue

            for box in entity.bounding_boxes:
                for other_box in other.bounding_boxes:
                    self.loop_counter += 1

                    if self.no_collision_possible(entity, other, box, other_box):
                        continue

                    self.do_collision_check(entity, other, box, other_box)

    def reset(self, game_data: GameData):
        self.log.debug(
            f"Looped {self.loop_counter} times and did {self.collision_counter} collision checks")
        self.loop_counter = 0
        self.collision_counter = 0


class PositionSystem(System):
    def __init__(self):
        super().__init__("Position", ['position', 'model_matrix'], [
            'velocity', 'rotation', 'scale', 'collision'])

    def run(self, game_data: GameData, entity):
        if hasattr(entity, 'velocity'):
            if hasattr(entity, 'collision'):
                entity.position += entity.collision
                del entity.collision
            entity.position += entity.velocity

        self.log.debug(f"{entity.position}")

        entity.model_matrix = identity()
        if hasattr(entity, 'scale'):
            scale(entity.model_matrix, entity.scale)

        if hasattr(entity, 'rotation'):
            if type(entity.rotation) == vec3:
                rotate(entity.model_matrix, entity.rotation)
            else:
                self.log.error(
                    f"Rotation is not vec3. Could not update model_matrix on {entity}")

        if type(entity.position) == vec3:
            translate(entity.model_matrix, entity.position)
        else:
            self.log.error(
                f"Position is not vec3. Could not update model_matrix on {entity}")

        for bbox in entity.bounding_boxes:
            m = identity()
            translate(m, bbox.position)
            if hasattr(entity, 'scale'):
                scale(m, entity.scale)
            translate(m, entity.position)
            bbox.model_matrix = m


class RenderSystem(System):
    def __init__(self):
        super().__init__("Render", ['asset'])
        self.render_calls = 0
        self.vertex_count = 0

    def reset(self, game_data: GameData):
        self.log.debug(f"{self.render_calls} render calls with {self.vertex_count} vertices")
        self.render_calls = 0
        self.vertex_count = 0

    def run(self, game_data: GameData, entity):
        self.render_calls += 1

        if not game_data.wireframe:
            entity.asset.current_index_buffer_id = 0
        else:
            entity.asset.current_index_buffer_id = 1 % len(entity.asset.index_buffers)

        if len(game_data.lights) != entity.asset.shader.number_of_lights:
            entity.asset.shader.compile(len(game_data.lights))

        entity.asset.shader.bind()

        self.bind_data(entity)
        self.bind_uniforms(entity, game_data)
        self.bind_texture(entity)

        self.draw(entity)

        entity.asset.shader.unbind()

    @staticmethod
    def bind_data(entity):
        glBindVertexArray(entity.asset.vertex_array_id)
        glBindBuffer(GL_ARRAY_BUFFER, entity.asset.vertex_buffer_id)
        for position, name, gl_type, size, stride, offset in entity.asset.attributes:
            glVertexAttribPointer(position, size, gl_type,
                                  GL_FALSE, stride, offset)
            glEnableVertexAttribArray(position)
            glBindAttribLocation(entity.asset.shader.handle,
                                 position, bytes(name, "utf-8"))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, entity.asset.index_buffers[entity.asset.current_index_buffer_id].id)

    def draw(self, entity):
        draw_count = entity.asset.index_buffers[entity.asset.current_index_buffer_id].draw_count
        glDrawElements(entity.asset.index_buffers[entity.asset.current_index_buffer_id].draw_type,
                       draw_count, GL_UNSIGNED_INT,
                       None)
        self.vertex_count += draw_count

    def bind_texture(self, entity):
        if entity.asset.texture is not None:
            texture_id = entity.asset.texture.id
            texture_unit = entity.asset.texture.texture_unit
            glActiveTexture(texture_unit)
            glBindTexture(GL_TEXTURE_2D, texture_id)

    def bind_uniforms(self, entity, game_data):
        for uniform_name in entity.asset.uniforms:
            data_name = entity.asset.uniforms[uniform_name]
            mapping = f"{uniform_name}=>{data_name}"
            if type(data_name) != str:
                self.log.debug(f"Found {mapping} in uniforms")
                # read data directly from uniforms
                data = data_name
                entity.asset.shader.uniform(uniform_name, data)
            elif hasattr(entity.asset, data_name):
                self.log.debug(f"Found {mapping} in asset")
                entity.asset.shader.uniform(
                    uniform_name, getattr(entity.asset, data_name))
            elif hasattr(entity, data_name):
                self.log.debug(f"Found {mapping} in entity")
                entity.asset.shader.uniform(
                    uniform_name, getattr(entity, data_name))
            elif hasattr(game_data, data_name):
                self.log.debug(f"Found {mapping} in game_data")
                entity.asset.shader.uniform(
                    uniform_name, getattr(game_data, data_name))
            else:
                self.log.warning(f"Could not find any data for {mapping}")


class BoundingBoxRenderSystem(System):
    def __init__(self):
        super().__init__("BoundingBoxRender", ['bounding_boxes'])

    def run(self, game_data: GameData, entity):
        if not game_data.collision_boxes:
            return

        for bb in entity.bounding_boxes:
            if hasattr(bb, 'asset'):
                game_data.systems['render'].run(game_data, bb)
