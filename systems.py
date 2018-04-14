import logging

from pyglet.gl import *

import logging_config
from game_data import GameData
from math_helper import identity, translate, vec3, rotate


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

    def run(self, game_data: GameData, entity):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


class InputSystem(System):
    def __init__(self):
        super().__init__("Input", [])


class AccelerationSystem(System):
    def __init__(self):
        super().__init__("Acceleration", [])


class CollisionSystem(System):
    def __init__(self):
        super().__init__("Collission", [])


class PositionSystem(System):
    def __init__(self):
        super().__init__("Position", ['position', 'model_matrix'], ['velocity', 'rotation'])
        self.log.setLevel(logging.DEBUG)

    def run(self, game_data: GameData, entity):
        if hasattr(entity, 'velocity'):
            entity.position += entity.velocity

        entity.model_matrix = identity()
        if type(entity.position) == vec3:
            translate(entity.model_matrix, entity.position)
        else:
            self.log.error(f"Position is not vec3. Could not update model_matrix on {entity}")

        if hasattr(entity, 'rotation'):
            if type(entity.rotation) == vec3:
                rotate(entity.model_matrix, entity.rotation)
            else:
                self.log.error(f"Rotation is not vec3. Could not update model_matrix on {entity}")


class RenderSystem(System):
    def __init__(self):
        super().__init__("Render", ['asset'])
        self.log.setLevel(logging.INFO)

    def run(self, game_data: GameData, entity):
        entity.asset.shader.bind()

        glBindVertexArray(entity.asset.vertex_array_id)

        glBindBuffer(GL_ARRAY_BUFFER, entity.asset.vertex_buffer_id)
        for position, name, gl_type, size, stride, offset in entity.asset.attributes:
            glVertexAttribPointer(position, size, gl_type, GL_FALSE, stride, offset)
            glEnableVertexAttribArray(position)
            glBindAttribLocation(entity.asset.shader.handle, position, bytes(name, "utf-8"))

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, entity.asset.index_buffer_id)

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
                entity.asset.shader.uniform(uniform_name, getattr(entity.asset, data_name))
            elif hasattr(entity, data_name):
                self.log.debug(f"Found {mapping} in entity")
                entity.asset.shader.uniform(uniform_name, getattr(entity, data_name))
            elif hasattr(game_data, data_name):
                self.log.debug(f"Found {mapping} in game_data")
                entity.asset.shader.uniform(uniform_name, getattr(game_data, data_name))
            else:
                self.log.warning(f"Could not find any data for {mapping}")

        if entity.asset.texture is not None:
            texture_id = entity.asset.texture.id
            texture_unit = entity.asset.texture.texture_unit
            glActiveTexture(texture_unit)
            glBindTexture(GL_TEXTURE_2D, texture_id)

        if entity.asset.use_index_buffer:
            glDrawElements(entity.asset.draw_type, entity.asset.draw_count, GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(entity.asset.draw_type, entity.asset.draw_start, entity.asset.draw_count)

        entity.asset.shader.unbind()
