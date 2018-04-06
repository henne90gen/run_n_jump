from ctypes import sizeof, c_float
from multiprocessing import Process, Value, Array

import noise
from pyglet.gl import *

from math_helper import vec3, timer, mat4, translate, rotate, identity
from shader import Shader


class TerrainShader(Shader):
    def __init__(self, terrain):
        super().__init__("terrain_vertex.glsl", "terrain_fragment.glsl")
        self.terrain = terrain

        self.vertex_array_id = GLuint()
        glGenVertexArrays(1, self.vertex_array_id)

        self.vertex_buffer_id = GLuint()
        glGenBuffers(1, self.vertex_buffer_id)

        self.index_buffer_id = GLuint()
        glGenBuffers(1, self.index_buffer_id)

    def upload_data(self, vertices, colors, normals, indices):
        vertex_data = []
        for i in range(0, len(vertices), 3):
            vertex_data.append(vertices[i])
            vertex_data.append(vertices[i + 1])
            vertex_data.append(vertices[i + 2])
            vertex_data.append(colors[i])
            vertex_data.append(colors[i + 1])
            vertex_data.append(colors[i + 2])
            vertex_data.append(normals[i])
            vertex_data.append(normals[i + 1])
            vertex_data.append(normals[i + 2])

        # noinspection PyCallingNonCallable,PyTypeChecker
        vertex_data_gl = (GLfloat * len(vertex_data))(*vertex_data)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        vertex_buffer_size = sizeof(vertex_data_gl)
        glBufferData(GL_ARRAY_BUFFER, vertex_buffer_size, vertex_data_gl, GL_STATIC_DRAW)

        # noinspection PyCallingNonCallable,PyTypeChecker
        index_data_gl = (GLint * len(indices))(*indices)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer_id)
        index_buffer_size = sizeof(index_data_gl)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_buffer_size, index_data_gl, GL_STATIC_DRAW)

        print(f"Uploaded {vertex_buffer_size} bytes of vertices and {index_buffer_size} bytes of indices")

    def bind(self, model_matrix, view_matrix, projection_matrix):
        super().bind()

        glBindVertexArray(self.vertex_array_id)

        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        stride = 9 * sizeof(c_float)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, 0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, 3 * sizeof(c_float))
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, 6 * sizeof(c_float))
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer_id)

        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"Error! {gluErrorString(error)}")

        glBindAttribLocation(self.handle, 0, bytes("a_Position", "utf-8"))
        glBindAttribLocation(self.handle, 1, bytes("a_Color", "utf-8"))
        glBindAttribLocation(self.handle, 2, bytes("a_Normal", "utf-8"))

        self.uniform_matrixf("u_Model", model_matrix)
        self.uniform_matrixf("u_View", view_matrix)
        self.uniform_matrixf("u_Projection", projection_matrix)

        self.uniformf("u_LightPosition", self.terrain.light_position.x, self.terrain.light_position.y,
                      self.terrain.light_position.z)
        self.uniformf("u_LightDirection", 0.0, -1.0, 0.0)

    def unbind(self):
        glBindVertexArray(0)
        super().unbind()


class Terrain:
    def __init__(self, width: int = 200, height: int = 200):
        self.width = width
        self.height = height
        self.position = vec3()
        self.rotation = vec3()
        self.color = vec3(255, 255, 255)
        self.step = 1
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.light_position = vec3(50, -10, 50)

        self.data_updated = Value("b", False)
        num_vertices = int((self.width / self.step) * (self.height / self.step) * 3)
        self.vertices = Array("f", num_vertices)
        self.colors = Array("f", num_vertices)
        self.normals = Array("f", num_vertices)
        num_indices = int((self.width / self.step - 1) * (self.height / self.step - 1) * 2 * 3)
        self.indices = Array("i", num_indices)
        print(f"Number of vertices: {num_vertices}, Number of indices: {num_indices}")

        self.shader = TerrainShader(self)
        self.regenerate_terrain()

    def regenerate_terrain(self):
        def func(*args):
            with timer():
                generate_vertices_and_indices(*args)

        args = (
            self.width, self.height, self.step, self.octaves, self.persistence, self.lacunarity, self.vertices,
            self.colors, self.normals, self.indices, self.data_updated
        )
        thread = Process(target=func, args=args)
        thread.start()

    def render(self, view_matrix: mat4, projection_matrix: mat4):
        if self.data_updated.value:
            self.shader.upload_data(self.vertices, self.colors, self.normals, self.indices)
            self.data_updated.value = False

        model_matrix = identity()
        translate(model_matrix, self.position)
        rotate(model_matrix, self.rotation)

        self.shader.bind(model_matrix, view_matrix, projection_matrix)

        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        self.shader.unbind()

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
    print("Generating terrain...")
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
            normal_aggregation[index_v1].append(normal)
            normal_aggregation[index_v2].append(normal)
            normal_aggregation[index_v3].append(normal)

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
            normal_aggregation[index_v1].append(normal)
            normal_aggregation[index_v2].append(normal)
            normal_aggregation[index_v3].append(normal)

    current_index = 0
    for i in range(len(normal_aggregation)):
        normal = sum(normal_aggregation[i], vec3()).normalize()
        if normal.y < 0:
            normal *= -1
        normals[current_index + 0] = normal.x
        normals[current_index + 1] = normal.y
        normals[current_index + 2] = normal.z
        current_index += 3

    print(f"Generated terrain using {len(vertices)} vertices and {len(indices) // 3} triangles")
    data_updated.value = True
