from ctypes import sizeof, c_float

from pyglet.gl import *

from math_helper import identity, translate, scale, vec3
from model import ModelAsset, load_blender_file, upload, ModelInstance, combine_attributes, add_mvp_uniforms, \
    add_light_uniforms
from shader import Shader


def cube(size, position: vec3, color: vec3):
    asset = ModelAsset()
    asset.shader = Shader("shaders/model_vertex.glsl", "shaders/model_fragment.glsl")
    stride = 6 * sizeof(c_float)
    attributes = [
        (0, 'a_Position', GL_FLOAT, 3, stride, 0),
        (1, 'a_Normal', GL_FLOAT, 3, stride, 3 * sizeof(c_float))
    ]
    asset.attributes = attributes

    vertices, normals, indices = load_blender_file("models/cube.obj")
    vertex_count = len(vertices) // 3
    asset.vertex_data = combine_attributes(vertex_count, (3, vertices), (3, normals))
    asset.indices = indices
    asset.draw_count = len(indices)
    upload(asset)

    add_mvp_uniforms(asset.uniforms)
    add_light_uniforms(asset.uniforms)
    asset.uniforms["u_Color"] = "color"

    model = ModelInstance()
    model.asset = asset
    model.color = color
    model.model_matrix = identity()
    scale(model.model_matrix, size)
    translate(model.model_matrix, position)
    return model
