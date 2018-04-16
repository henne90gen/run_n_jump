from ctypes import sizeof, c_float

from pyglet.gl import *

from math_helper import vec3, translate
from model import ModelAsset, load_blender_file, upload, ModelInstance, combine_attributes, add_mvp_uniforms, \
    add_light_uniforms, BoundingBox
from shader import Shader


def generate_bounding_box(vertices_in: list, normals: list):
    vertices = []
    for i in range(0, len(vertices_in), 3):
        vertex = vec3(vertices_in[i], vertices_in[i + 1], vertices_in[i + 2])
        vertices.append(vertex)

    box = BoundingBox()
    box.vertices = vertices
    box.normals = normals
    return box


def cube(size, position: vec3, color: vec3):
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
    vertex_count = len(vertices) // 3
    asset.vertex_data = combine_attributes(vertex_count, (3, vertices), (3, normals))
    asset.indices = indices
    asset.draw_count = len(indices)
    upload(asset)

    add_mvp_uniforms(asset.uniforms)
    add_light_uniforms(asset.uniforms)
    asset.uniforms["u_Color"] = "color"

    model = ModelInstance()
    model.name = "Cube" + str(position)
    model.asset = asset
    model.bounding_boxes = [generate_bounding_box(vertices, all_normals)]
    model.position = position
    translate(model.model_matrix, model.position)
    model.scale = size
    return model
