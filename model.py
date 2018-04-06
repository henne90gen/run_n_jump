from ctypes import c_float, sizeof

from pyglet.gl import *

from math_helper import vec3, identity, translate, rotate
from render_data import RenderData
from shader import Shader


class ModelShader(Shader):
    def __init__(self, model, path_prefix):
        super().__init__(f"{path_prefix}model_vertex.glsl", f"{path_prefix}model_fragment.glsl")
        self.model = model

        self.index_count = 0

        self.vertex_array_id = GLuint()
        glGenVertexArrays(1, self.vertex_array_id)

        self.vertex_buffer_id = GLuint()
        glGenBuffers(1, self.vertex_buffer_id)

        self.index_buffer_id = GLuint()
        glGenBuffers(1, self.index_buffer_id)

    def upload_data(self, vertices: list, colors: list, normals: list, indices: list):
        self.index_count = len(indices)

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

    def bind(self, model_matrix, view_matrix, projection_matrix, light_position, light_direction):
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

        self.uniformf("u_LightPosition", *light_position)
        self.uniformf("u_LightDirection", *light_direction)

    def unbind(self):
        glBindVertexArray(0)
        super().unbind()


class Model:
    def __init__(self, path_prefix: str = ""):
        self.shader = ModelShader(self, path_prefix)
        self.position = vec3()
        self.rotation = vec3()

    def render(self, render_data: RenderData):
        model_matrix = identity()
        translate(model_matrix, self.position)
        rotate(model_matrix, self.rotation)

        self.shader.bind(model_matrix, render_data.view_matrix, render_data.projection_matrix,
                         render_data.light_position, render_data.light_direction)

        glDrawElements(GL_TRIANGLES, self.shader.index_count, GL_UNSIGNED_INT, None)

        self.shader.unbind()


def load_model(path: str, shader_path_prefix: str = ""):
    with open(path, "r") as f:
        lines = f.readlines()

    vertices = []
    all_normals = []
    faces = []
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("#"):
            continue
        elif line_strip.startswith("vn"):
            all_normals.append(line_strip)
        elif line_strip.startswith("v"):
            vertices.append(line_strip)
        elif line_strip.startswith("f"):
            faces.append(line_strip)

    vertices = list(
        map(lambda x: list(map(float, x[2:].split())), vertices)
    )
    vertices = [item for sublist in vertices for item in sublist]

    all_normals = list(
        map(lambda x: vec3(arr=list(map(float, x[3:].split()))), all_normals)
    )

    normals = [vec3() for _ in range(len(vertices) // 3)]

    indices = []
    for face in faces:
        points = face.strip()[2:].split()
        for p in points:
            parts = p.split("/")
            index = int(parts[0]) - 1
            indices.append(index)
            normal_index = int(parts[2]) - 1
            normals[index] += all_normals[normal_index]

    normals = [item for sublist in normals for item in sublist]

    colors = [1.0 for _ in vertices]

    model = Model(shader_path_prefix)
    model.shader.upload_data(vertices, colors, normals, indices)

    return model