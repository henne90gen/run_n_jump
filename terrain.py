from ctypes import sizeof, c_float

import noise
from pyglet.gl import *

import math_helper
from graphics import rotate, translate, identity, shader
from math_helper import vec3, timer, mat4
from shader import Shader


class TerrainShader(Shader):
    def __init__(self):
        super().__init__("terrain_vertex.glsl", "terrain_fragment.glsl")

    def bind(self):
        super().bind()

        glBindAttribLocation(self.handle, 0, bytes("a_Position", "utf-8"))
        glBindAttribLocation(self.handle, 1, bytes("a_Color", "utf-8"))
        glBindAttribLocation(self.handle, 2, bytes("a_Normal", "utf-8"))


class Terrain:
    def __init__(self, width: int = 200, height: int = 200):
        self.width = width
        self.height = height
        self.position = vec3()
        self.rotation = vec3()
        self.vertices = []
        self.indices = []
        self.color = vec3(255, 255, 255)
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0

        self.vertex_array_id = GLuint()
        glGenVertexArrays(1, self.vertex_array_id)

        self.vertex_buffer_id = GLuint()
        glGenBuffers(1, self.vertex_buffer_id)

        self.index_buffer_id = GLuint()
        glGenBuffers(1, self.index_buffer_id)

        self.shader = TerrainShader()
        self.regenerate_terrain()

    def regenerate_terrain(self):
        with timer():
            self.generate_vertices_and_indices()
            self.upload_data()

    def upload_data(self):
        vertex_data = []
        for v, c, n in self.vertices:
            vertex_data.append(v.x)
            vertex_data.append(v.y)
            vertex_data.append(v.z)
            vertex_data.append(c.x)
            vertex_data.append(c.y)
            vertex_data.append(c.z)
            vertex_data.append(n.x)
            vertex_data.append(n.y)
            vertex_data.append(n.z)

        # noinspection PyCallingNonCallable,PyTypeChecker
        vertex_data_gl = (GLfloat * len(vertex_data))(*vertex_data)

        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        vertex_buffer_size = sizeof(vertex_data_gl)
        glBufferData(GL_ARRAY_BUFFER, vertex_buffer_size, vertex_data_gl, GL_STATIC_DRAW)

        # noinspection PyCallingNonCallable,PyTypeChecker
        index_data_gl = (GLint * len(self.indices))(*self.indices)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer_id)
        index_buffer_size = sizeof(index_data_gl)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_buffer_size, index_data_gl, GL_STATIC_DRAW)

        print(f"Uploaded {vertex_buffer_size} bytes of vertices and {index_buffer_size} bytes of indices")

    def generate_vertices_and_indices(self):
        print("Generating terrain...")
        self.vertices = []
        normals = []
        step = 10
        scale = 100.0
        for row in range(0, self.height, step):
            for col in range(0, self.width, step):
                y = noise.pnoise2(col / scale,
                                  row / scale,
                                  octaves=self.octaves,
                                  persistence=self.persistence,
                                  lacunarity=self.lacunarity,
                                  repeatx=self.width,
                                  repeaty=self.height,
                                  base=0)
                c = y + 0.5
                y *= 75
                y -= 30
                position = vec3(col, y, row)
                # color = vec3(random.random(), random.random(), random.random())
                color = vec3(c, c, c)
                vertex = (position, color, vec3(1.0))
                self.vertices.append(vertex)
                normals.append([])

        self.indices = []
        for row in range(self.height // step - 1):
            for col in range(self.width // step - 1):
                # top left
                index_v1 = row * self.width // step + col
                self.indices.append(index_v1)
                v1 = self.vertices[index_v1][0]

                index_v2 = (row + 1) * self.width // step + col
                self.indices.append(index_v2)
                v2 = self.vertices[index_v2][0]

                index_v3 = row * self.width // step + col + 1
                self.indices.append(index_v3)
                v3 = self.vertices[index_v3][0]

                normal = v1.calculate_normal(v2, v3)
                normals[index_v1].append(normal)
                normals[index_v2].append(normal)
                normals[index_v3].append(normal)

                # bottom right
                index_v1 = row * self.width // step + col + 1
                self.indices.append(index_v1)
                v1 = self.vertices[index_v1][0]

                index_v2 = (row + 1) * self.width // step + col
                self.indices.append(index_v2)
                v2 = self.vertices[index_v2][0]

                index_v3 = (row + 1) * self.width // step + col + 1
                self.indices.append(index_v3)
                v3 = self.vertices[index_v3][0]

                normal = v1.calculate_normal(v2, v3)
                normals[index_v1].append(normal)
                normals[index_v2].append(normal)
                normals[index_v3].append(normal)

        normals = list(map(lambda x: sum(x, vec3()).normalize(), normals))

        for index, normal in enumerate(normals):
            if normal.y < 0:
                normal *= -1
            self.vertices[index][2].x = normal.x
            self.vertices[index][2].y = normal.y
            self.vertices[index][2].z = normal.z

        print(f"Generated terrain using {len(self.vertices)} vertices and {len(self.indices) // 3} triangles")

    def render(self, view_matrix: mat4, projection_matrix: mat4):
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
            print("Error!", gluErrorString(error))

        model_matrix = math_helper.identity()
        math_helper.translate(model_matrix, self.position)
        math_helper.rotate(model_matrix, self.rotation)

        self.shader.bind()
        self.shader.uniform_matrixf("u_Model", model_matrix)
        self.shader.uniform_matrixf("u_View", view_matrix)
        self.shader.uniform_matrixf("u_Projection", projection_matrix)

        self.shader.uniformf("u_LightPosition", 20.0, 20.0, 20.0)
        self.shader.uniformf("u_LightDirection", 0.0, -1.0, 0.0)

        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

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
