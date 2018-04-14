from pyglet.gl import *

from game_data import GameData


class System:
    def __init__(self):
        self.components = []
        self.name = "System"

    def supports(self, entity):
        for component in self.components:
            if not hasattr(entity, component):
                return False
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


class RenderSystem(System):
    def __init__(self):
        super().__init__()
        self.components = ['asset']
        self.name = "Renderer"

    @staticmethod
    def run(game_data: GameData, entity):
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
            if type(data_name) != str:
                print("Found", data_name, "in uniforms")
                # read data directly from uniforms
                data = data_name
                entity.asset.shader.uniform(uniform_name, data)
            elif hasattr(entity.asset, data_name):
                print("Found", data_name, "in asset")
                entity.asset.shader.uniform(uniform_name, getattr(entity.asset, data_name))
            elif hasattr(entity, data_name):
                print("Found", data_name, "in entity")
                entity.asset.shader.uniform(uniform_name, getattr(entity, data_name))
            elif hasattr(game_data, data_name):
                print("Found", data_name, "in game_data")
                entity.asset.shader.uniform(uniform_name, getattr(game_data, data_name))
            else:
                print("Could not find any data for", uniform_name)

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
