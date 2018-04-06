from multiprocessing import Process, Value, Array

import noise
from pyglet.gl import *

from math_helper import vec3, timer
from model import Model
from render_data import RenderData


class Terrain:
    def __init__(self, width: int = 200, height: int = 200):
        self.width = width
        self.height = height
        self.color = vec3(255, 255, 255)
        self.step = 10
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 0  # 2.0

        self.data_updated = Value("b", False)
        num_vertices = int((self.width / self.step) * (self.height / self.step) * 3)
        self.vertices = Array("f", num_vertices, lock=False)
        self.colors = Array("f", num_vertices, lock=False)
        self.normals = Array("f", num_vertices, lock=False)
        num_indices = int((self.width / self.step - 1) * (self.height / self.step - 1) * 2 * 3)
        self.indices = Array("i", num_indices, lock=False)

        self.model = Model()

        self.regenerate_terrain()

    def regenerate_terrain(self):
        # def func(*args):
        #     with timer():
        #         generate_vertices_and_indices(*args)

        arguments = (
            self.width, self.height, self.step, self.octaves, self.persistence, self.lacunarity, self.vertices,
            self.colors, self.normals, self.indices, self.data_updated
        )
        thread = Process(target=generate_vertices_and_indices, args=arguments)
        thread.start()

    def render(self, render_data: RenderData):
        if self.data_updated.value:
            self.model.shader.upload_data(self.vertices, self.colors, self.normals, self.indices)
            self.data_updated.value = False
            self.lacunarity += 10 * render_data.frame_time
            if self.lacunarity > 5:
                self.lacunarity = 0
            self.regenerate_terrain()

        self.model.render(render_data)

    def handle_key(self, symbol, pressed):
        if not pressed:
            changed = False
            if symbol == pyglet.window.key.C:
                self.octaves += 1
                changed = True
            elif symbol == pyglet.window.key.V:
                self.octaves -= 1
                if self.octaves <= 0:
                    self.octaves = 1
                changed = True
            if symbol == pyglet.window.key.Y:
                self.lacunarity += 0.1
                changed = True
            elif symbol == pyglet.window.key.X:
                self.lacunarity -= 0.1
                changed = True

            if changed:
                print(f"Octaves: {self.octaves}")
                print(f"Lacunarity: {self.lacunarity}")
                self.regenerate_terrain()


def generate_vertices_and_indices(width, height, step, octaves, persistence, lacunarity, vertices: Array, colors: Array,
                                  normals: Array, indices: Array, data_updated: Value):
    # print("Generating terrain...")
    scale = 100.0
    normal_aggregation = []
    for row in range(0, height, step):
        for col in range(0, width, step):
            y = noise.pnoise2(col / scale,
                              row / scale,
                              octaves=octaves,
                              persistence=persistence,
                              lacunarity=lacunarity,
                              repeatx=width,
                              repeaty=height,
                              base=0)
            y *= 75
            y -= 30
            position = vec3(col, y, row)
            color = vec3(1, 1, 1)
            index = int(row / step * (width / step * 3) + col / step * 3)
            vertices[index + 0] = position.x
            vertices[index + 1] = position.y
            vertices[index + 2] = position.z
            colors[index + 0] = color.x
            colors[index + 1] = color.y
            colors[index + 2] = color.z
            normals[index + 0] = 0
            normals[index + 1] = 0
            normals[index + 2] = 0
            normal_aggregation.append([])

    current_index = 0
    for row in range(height // step - 1):
        for col in range(width // step - 1):
            # top left
            index_v1 = row * width // step + col
            indices[current_index] = index_v1
            current_index += 1
            v1 = vec3(vertices[index_v1 * 3], vertices[index_v1 * 3 + 1], vertices[index_v1 * 3 + 2])

            index_v2 = (row + 1) * width // step + col
            indices[current_index] = index_v2
            current_index += 1
            v2 = vec3(vertices[index_v2 * 3], vertices[index_v2 * 3 + 1], vertices[index_v2 * 3 + 2])

            index_v3 = row * width // step + col + 1
            indices[current_index] = index_v3
            current_index += 1
            v3 = vec3(vertices[index_v3 * 3], vertices[index_v3 * 3 + 1], vertices[index_v3 * 3 + 2])

            normal = v1.calculate_normal(v2, v3)
            normals[index_v1 * 3] += normal.x
            normals[index_v1 * 3 + 1] += normal.y
            normals[index_v1 * 3 + 2] += normal.z
            normals[index_v2 * 3] += normal.x
            normals[index_v2 * 3 + 1] += normal.y
            normals[index_v2 * 3 + 2] += normal.z
            normals[index_v3 * 3] += normal.x
            normals[index_v3 * 3 + 1] += normal.y
            normals[index_v3 * 3 + 2] += normal.z

            # bottom right
            index_v1 = row * width // step + col + 1
            indices[current_index] = index_v1
            current_index += 1
            v1 = vec3(vertices[index_v1 * 3], vertices[index_v1 * 3 + 1], vertices[index_v1 * 3 + 2])

            index_v2 = (row + 1) * width // step + col
            indices[current_index] = index_v2
            current_index += 1
            v2 = vec3(vertices[index_v2 * 3], vertices[index_v2 * 3 + 1], vertices[index_v2 * 3 + 2])

            index_v3 = (row + 1) * width // step + col + 1
            indices[current_index] = index_v3
            current_index += 1
            v3 = vec3(vertices[index_v3 * 3], vertices[index_v3 * 3 + 1], vertices[index_v3 * 3 + 2])

            normal = v1.calculate_normal(v2, v3)
            normals[index_v1 * 3] += normal.x
            normals[index_v1 * 3 + 1] += normal.y
            normals[index_v1 * 3 + 2] += normal.z
            normals[index_v2 * 3] += normal.x
            normals[index_v2 * 3 + 1] += normal.y
            normals[index_v2 * 3 + 2] += normal.z
            normals[index_v3 * 3] += normal.x
            normals[index_v3 * 3 + 1] += normal.y
            normals[index_v3 * 3 + 2] += normal.z

    # print(f"Generated terrain using {len(vertices) // 3} vertices and {len(indices) // 3} triangles")
    data_updated.value = True
