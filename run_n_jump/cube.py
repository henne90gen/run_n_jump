from ctypes import sizeof, c_float

from pyglet.gl import *

from .math_helper import vec3, translate, scale
from .model import ModelAsset, load_blender_file, upload, ModelInstance, add_mvp_uniforms, \
    add_light_uniforms, BoundingBox, IndexBuffer
from .shader import Shader


def generate_bounding_box(vertices_in: list, normals: list):
    vertices = []
    for i in range(0, len(vertices_in), 3):
        vertex = vec3(vertices_in[i], vertices_in[i + 1], vertices_in[i + 2])
        vertices.append(vertex)

    box = BoundingBox()
    box.vertices = vertices
    box.normals = normals
    box.radius = max(map(lambda v: v.length, box.vertices))
    return box


def cube_asset(color: vec3):
    asset = ModelAsset()
    asset.color = color
    asset.shader = Shader("shaders/model_vertex.glsl", "shaders/model_fragment.glsl")
    stride = 6 * sizeof(c_float)
    attributes = [
        (0, 'a_Position', GL_FLOAT, 3, stride, 0),
        (1, 'a_Normal', GL_FLOAT, 3, stride, 3 * sizeof(c_float))
    ]
    asset.attributes = attributes

    vertices, normals, indices, all_normals = load_blender_file("models/cube.obj")

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
    return asset, vertices, all_normals


def cube(size, position: vec3, color: vec3):
    model = ModelInstance()
    model.name = "Cube" + str(position)
    asset, vertices, normals = cube_asset(color)

    model.asset = asset
    model.bounding_boxes = [generate_bounding_box(vertices, normals)]
    model.scale = size
    model.position = position
    scale(model.model_matrix, model.scale)
    translate(model.model_matrix, model.position)

    model.systems = [
        'position',
        'render'
    ]
    return model
