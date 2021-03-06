from ctypes import sizeof

from pyglet.gl import GLuint, glGenTextures, glGenBuffers, glGenVertexArrays, GL_STATIC_DRAW, GLint, GLfloat
from pyglet.gl import glBindTexture, GL_TEXTURE_2D, glTexParameterf, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_TEXTURE_MIN_FILTER
from pyglet.gl import glTexImage2D, GL_ALPHA, GLubyte, glBindBuffer, glBufferData, GL_ELEMENT_ARRAY_BUFFER, GL_ARRAY_BUFFER
from pyglet.gl import GL_TRIANGLES, GL_LINES

from .math_helper import identity, vec3


class Texture:
    texture_unit = None
    width = -1
    height = -1
    buffer = None
    format = None
    type = None

    attributes = None

    def __init__(self):
        self.id = GLuint()
        glGenTextures(1, self.id)

        self.attributes = {}


class IndexBuffer:
    draw_type = None
    draw_count = -1
    id = -1

    def __init__(self):
        self.indices = []
        self.id = GLuint()
        glGenBuffers(1, self.id)


class ModelAsset:
    shader = None
    texture = None
    color = None

    vertex_array_id = -1
    vertex_buffer_id = -1
    index_buffers = None
    current_index_buffer_id = -1

    attributes = None
    attribute_data = None
    uniforms = None

    def __init__(self):
        self.color = vec3(1.0, 1.0, 1.0)

        self.attributes = []
        self.attribute_data = {}
        self.uniforms = {}

        self.current_index_buffer_id = 0
        self.index_buffers = []


class BoundingBox:
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.position = vec3()
        self.model_matrix = identity()
        self.type = 'static'


class ModelInstance:
    asset: ModelAsset = None
    model_matrix = None
    name = "ModelInstance"

    def __init__(self):
        self.model_matrix = identity()
        self.bounding_boxes = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


def add_mvp_uniforms(uniforms):
    uniforms['u_Model'] = "model_matrix"
    uniforms['u_View'] = "view_matrix"
    uniforms['u_Projection'] = "projection_matrix"


def add_light_uniforms(uniforms):
    uniforms['u_Lights'] = "lights"
    uniforms['u_LightDirection'] = "light_direction"


def add_texture_uniform(uniforms):
    uniforms['u_TextureSampler'] = 0


def combine_attributes(vertex_count, *attributes):
    vertex_data = []
    for i in range(vertex_count):
        for size, attribute_array in attributes:
            for j in range(size):
                vertex_data.append(attribute_array[i * size + j])
    return vertex_data


def upload(asset: ModelAsset, gl_usage=GL_STATIC_DRAW):
    asset.vertex_array_id = GLuint()
    glGenVertexArrays(1, asset.vertex_array_id)

    asset.vertex_buffer_id = GLuint()
    glGenBuffers(1, asset.vertex_buffer_id)

    upload_vertices(asset, gl_usage)

    upload_indices(asset, gl_usage)

    if asset.texture is not None:
        glBindTexture(GL_TEXTURE_2D, asset.texture.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        # noinspection PyCallingNonCallable,PyTypeChecker
        texture_data = (GLubyte * len(asset.texture.buffer.flat)
                        )(*asset.texture.buffer.flatten())
        glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, asset.texture.width, asset.texture.height, 0, asset.texture.format,
                     asset.texture.type, texture_data)


def upload_indices(asset: ModelAsset, gl_usage=GL_STATIC_DRAW):
    for buffer in asset.index_buffers:
        # noinspection PyCallingNonCallable,PyTypeChecker
        index_data_gl = (GLint * len(buffer.indices))(*buffer.indices)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffer.id)
        index_buffer_size = sizeof(index_data_gl)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     index_buffer_size, index_data_gl, gl_usage)


def upload_vertices(asset: ModelAsset, gl_usage=GL_STATIC_DRAW):
    vertex_count = -1
    data = []
    for key in asset.attribute_data:
        value = asset.attribute_data[key]
        data.append(value)
        if vertex_count == -1:
            vertex_count = len(value[1]) // value[0]
    if vertex_count == -1:
        vertex_count = 0

    vertex_data = combine_attributes(vertex_count, *data)

    # noinspection PyCallingNonCallable,PyTypeChecker
    vertex_data_gl = (GLfloat * len(vertex_data))(*vertex_data)
    glBindBuffer(GL_ARRAY_BUFFER, asset.vertex_buffer_id)
    vertex_buffer_size = sizeof(vertex_data_gl)
    glBufferData(GL_ARRAY_BUFFER, vertex_buffer_size, vertex_data_gl, gl_usage)


def load_blender_file(path):
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

    triangle_indices = []
    for face in faces:
        points = face.strip()[2:].split()
        for p in points:
            parts = p.split("/")
            index = int(parts[0]) - 1
            triangle_indices.append(index)
            normal_index = int(parts[2]) - 1
            normals[index] += all_normals[normal_index]

    indices.append((GL_TRIANGLES, triangle_indices))
    indices.append((GL_LINES, get_line_indices(triangle_indices)))

    normals = [item for sublist in normals for item in sublist]
    return vertices, normals, indices, all_normals


def get_line_indices(triangle_indices):
    indices = []
    for i in range(0, len(triangle_indices), 3):
        indices.extend([
            triangle_indices[i], triangle_indices[i + 1],
            triangle_indices[i + 1], triangle_indices[i + 2],
            triangle_indices[i + 2], triangle_indices[i],
        ])
    return indices
