from ctypes import c_float, sizeof

import numpy as np
from PIL import Image
from pyglet.gl import *

from math_helper import identity, vec3, translate
from model import ModelAsset, ModelInstance, upload, combine_attributes, add_mvp_uniforms, add_light_uniforms
from shader import Shader


def load_image(filename: str):
    labyrinth_map = Image.open(filename)
    width = labyrinth_map.width
    height = labyrinth_map.height
    image_array = np.asarray(labyrinth_map).flatten()
    map_array = np.zeros((width, height))
    for row in range(height):
        for col in range(1, width * 2, 2):
            map_array[row, (col - 1) // 2] = image_array[row * width * 2 + col]
    return map_array


def generate_vertices(arr: np.ndarray):
    vertices = []
    normals = []
    indices = []
    bounding_boxes = []

    def add_quad_to_index():
        index = len(indices)
        indices.extend([index, index + 1, index + 2, index + 3, index + 4, index + 5])

    def floor(x: float, y: float, normal_direction: float, position: float, scale: float):
        add_quad_to_index()

        normal = [0, normal_direction, 0]
        for _ in range(6):
            normals.extend(normal)

        vertices.extend([x * scale, position, y * scale])
        vertices.extend([(x + 1) * scale, position, y * scale])
        vertices.extend([(x + 1) * scale, position, (y + 1) * scale])

        vertices.extend([x * scale, position, y * scale])
        vertices.extend([(x + 1) * scale, position, (y + 1) * scale])
        vertices.extend([x * scale, position, (y + 1) * scale])

    def front(x: float, y: float, z: float, scale: float, normal_direction: float):
        add_quad_to_index()

        normal = [0, 0, normal_direction]
        for _ in range(6):
            normals.extend(normal)

        vertices.extend([x * scale, y * scale, z * scale])
        vertices.extend([(x + 1) * scale, y * scale, z * scale])
        vertices.extend([(x + 1) * scale, (y + 1) * scale, z * scale])

        vertices.extend([x * scale, y * scale, z * scale])
        vertices.extend([(x + 1) * scale, (y + 1) * scale, z * scale])
        vertices.extend([x * scale, (y + 1) * scale, z * scale])

    def left(x: float, y: float, z: float, scale: float, normal_direction: float):
        add_quad_to_index()

        normal = [normal_direction, 0, 0]
        for _ in range(6):
            normals.extend(normal)

        vertices.extend([x * scale, y * scale, z * scale])
        vertices.extend([x * scale, y * scale, (z + 1) * scale])
        vertices.extend([x * scale, (y + 1) * scale, (z + 1) * scale])

        vertices.extend([x * scale, y * scale, z * scale])
        vertices.extend([x * scale, (y + 1) * scale, (z + 1) * scale])
        vertices.extend([x * scale, (y + 1) * scale, z * scale])

    for row in range(arr.shape[1]):
        for col in range(arr.shape[0]):
            color = arr[row, col]
            if color == 255:
                s = 10
                floor(col, row, -1, 10, s)
                floor(col, row, 1, 0, s)

                if arr[row + 1, col] != 255:
                    front(col, 0, row + 1, s, -1)
                if arr[row - 1, col] != 255:
                    front(col, 0, row, s, 1)

                if arr[row, col - 1] != 255:
                    left(col, 0, row, s, 1)
                if arr[row, col + 1] != 255:
                    left(col + 1, 0, row, s, -1)

    return vertices, normals, indices, bounding_boxes


def labyrinth():
    asset = ModelAsset()
    asset.shader = Shader("shaders/model_vertex.glsl", "shaders/model_fragment.glsl")
    stride = 6 * sizeof(c_float)
    attributes = [
        (0, 'a_Position', GL_FLOAT, 3, stride, 0),
        (1, 'a_Normal', GL_FLOAT, 3, stride, 3 * sizeof(c_float))
    ]
    asset.attributes = attributes

    image_array = load_image("labyrinth.png")
    vertices, normals, indices, bounding_boxes = generate_vertices(image_array)
    asset.vertex_data = combine_attributes(len(vertices) // 3, (3, vertices), (3, normals))
    asset.indices = indices
    asset.draw_count = len(indices)
    upload(asset)

    add_mvp_uniforms(asset.uniforms)
    add_light_uniforms(asset.uniforms)
    asset.uniforms["u_Color"] = "color"

    model = ModelInstance()
    model.name = "Labyrinth"
    model.asset = asset
    model.bounding_boxes = bounding_boxes
    model.model_matrix = identity()
    translate(model.model_matrix, vec3(0, -5, 0))
    return model
