from ctypes import c_float, sizeof

from pyglet.gl import *

from math_helper import vec3
from model import ModelAsset, IndexBuffer, upload, add_mvp_uniforms, add_light_uniforms, \
    get_line_indices
from shader import Shader


def rectangular_prism_vertices(size: vec3):
    vertices = []
    normals = []
    indices = []

    # front
    vertices.extend([size.x, size.y, size.z])
    vertices.extend([-size.x, -size.y, size.z])
    vertices.extend([size.x, -size.y, size.z])
    vertices.extend([size.x, size.y, size.z])
    vertices.extend([-size.x, size.y, size.z])
    vertices.extend([-size.x, -size.y, size.z])
    for i in range(6):
        normals.extend([0, 0, 1])

    # right
    vertices.extend([size.x, size.y, size.z])
    vertices.extend([size.x, -size.y, -size.z])
    vertices.extend([size.x, size.y, -size.z])
    vertices.extend([size.x, size.y, size.z])
    vertices.extend([size.x, -size.y, size.z])
    vertices.extend([size.x, -size.y, -size.z])
    for i in range(6):
        normals.extend([1, 0, 0])

    # back
    vertices.extend([size.x, size.y, -size.z])
    vertices.extend([size.x, -size.y, -size.z])
    vertices.extend([-size.x, -size.y, -size.z])
    vertices.extend([size.x, size.y, -size.z])
    vertices.extend([-size.x, -size.y, -size.z])
    vertices.extend([-size.x, size.y, -size.z])
    for i in range(6):
        normals.extend([0, 0, -1])

    # left
    vertices.extend([-size.x, size.y, size.z])
    vertices.extend([-size.x, size.y, -size.z])
    vertices.extend([-size.x, -size.y, -size.z])
    vertices.extend([-size.x, size.y, size.z])
    vertices.extend([-size.x, -size.y, -size.z])
    vertices.extend([-size.x, -size.y, size.z])
    for i in range(6):
        normals.extend([-1, 0, 0])

    # top
    vertices.extend([size.x, size.y, size.z])
    vertices.extend([size.x, size.y, -size.z])
    vertices.extend([-size.x, size.y, size.z])
    vertices.extend([-size.x, size.y, size.z])
    vertices.extend([size.x, size.y, -size.z])
    vertices.extend([-size.x, size.y, -size.z])
    for i in range(6):
        normals.extend([0, 1, 0])

    # bottom
    vertices.extend([size.x, -size.y, size.z])
    vertices.extend([-size.x, -size.y, size.z])
    vertices.extend([size.x, -size.y, -size.z])
    vertices.extend([-size.x, -size.y, size.z])
    vertices.extend([-size.x, -size.y, -size.z])
    vertices.extend([size.x, -size.y, -size.z])
    for i in range(6):
        normals.extend([0, -1, 0])

    for i in range(0, len(vertices), 3):
        indices.append(i // 3)

    return vertices, normals, [(GL_TRIANGLES, indices), (GL_LINES, get_line_indices(indices))]


def rectangular_prism(color: vec3, vertices, normals, indices):
    asset = ModelAsset()
    asset.color = color
    asset.shader = Shader("shaders/model_vertex.glsl", "shaders/model_fragment.glsl")
    stride = 6 * sizeof(c_float)
    attributes = [
        (0, 'a_Position', GL_FLOAT, 3, stride, 0),
        (1, 'a_Normal', GL_FLOAT, 3, stride, 3 * sizeof(c_float))
    ]
    asset.attributes = attributes

    asset.attribute_data = {'vertices': (3, vertices), 'normals': (3, normals)}

    for draw_type, values in indices:
        index_buffer = IndexBuffer()
        index_buffer.draw_type = draw_type
        index_buffer.draw_count = len(values)
        index_buffer.indices = values
        asset.index_buffers.append(index_buffer)

    upload(asset)

    add_mvp_uniforms(asset.uniforms)
    add_light_uniforms(asset.uniforms)
    asset.uniforms["u_Color"] = "color"
    return asset
