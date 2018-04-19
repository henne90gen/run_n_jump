from ctypes import c_float, sizeof

import numpy as np
from PIL import Image
from pyglet.gl import *

from cube import cube
from math_helper import identity, vec3, translate, scale
from model import ModelAsset, ModelInstance, upload, combine_attributes, add_mvp_uniforms, add_light_uniforms, \
    BoundingBox, IndexBuffer
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
    cube_normals = [vec3(1), vec3(-1), vec3(0, 1), vec3(0, -1), vec3(0, 0, 1), vec3(0, 0, -1)]
    cube_vertices = [
        vec3(1, 1, 1), vec3(0, 1, 1),
        vec3(1, 0, 1), vec3(1, 1, 0),
        vec3(1, 0, 0), vec3(0, 1, 0),
        vec3(0, 0, 1), vec3(0, 0, 0)
    ]

    vertices = []
    normals = []
    indices = []
    bounding_boxes = []

    def add_quad_to_index():
        index = len(indices)
        indices.extend([index, index + 1, index + 2, index + 3, index + 4, index + 5])

    def floor(x: float, y: float, normal_direction: float, position: float):
        add_quad_to_index()

        normal = [0, normal_direction, 0]
        for _ in range(6):
            normals.extend(normal)

        vertices.extend([x, position, y])
        vertices.extend([(x + 1), position, y])
        vertices.extend([(x + 1), position, (y + 1)])

        vertices.extend([x, position, y])
        vertices.extend([(x + 1), position, (y + 1)])
        vertices.extend([x, position, (y + 1)])

    def front(x: float, y: float, z: float, normal_direction: float):
        add_quad_to_index()

        normal = [0, 0, normal_direction]
        for _ in range(6):
            normals.extend(normal)

        vertices.extend([x, y, z])
        vertices.extend([(x + 1), y, z])
        vertices.extend([(x + 1), (y + 1), z])

        vertices.extend([x, y, z])
        vertices.extend([(x + 1), (y + 1), z])
        vertices.extend([x, (y + 1), z])

        if normal_direction == 1:
            box = BoundingBox()
            box.normals = cube_normals.copy()
            position = vec3(x, y, z - normal_direction)
            box.vertices = list(map(lambda v: v + position, cube_vertices.copy()))
            offset = vec3(0.5, 0, 0.5)
            model = cube(5, (position + offset) * 10, vec3(1, 1, 1))
            model.asset.model_matrix = model.model_matrix
            box.asset = model.asset
            bounding_boxes.append(box)

    def left(x: float, y: float, z: float, normal_direction: float):
        add_quad_to_index()

        normal = [normal_direction, 0, 0]
        for _ in range(6):
            normals.extend(normal)

        vertices.extend([x, y, z])
        vertices.extend([x, y, (z + 1)])
        vertices.extend([x, (y + 1), (z + 1)])

        vertices.extend([x, y, z])
        vertices.extend([x, (y + 1), (z + 1)])
        vertices.extend([x, (y + 1), z])

    for row in range(arr.shape[1]):
        for col in range(arr.shape[0]):
            color = arr[row, col]
            if color == 255:
                floor(col, row, -1, 1)
                floor(col, row, 1, 0)

                if arr[row + 1, col] != 255:
                    front(col, 0, row + 1, -1)
                if arr[row - 1, col] != 255:
                    front(col, 0, row, 1)

                if arr[row, col - 1] != 255:
                    left(col, 0, row, 1)
                if arr[row, col + 1] != 255:
                    left(col + 1, 0, row, -1)

    # x, y, z = 0, 0, 0
    # box = BoundingBox()
    # box.normals = cube_normals.copy()
    # position = vec3(x, y - 0.5, z - 1)
    # box.vertices = list(map(lambda v: v + position, cube_vertices.copy()))
    # bounding_boxes.append(box)
    # x, y, z = 1, 0, 0
    # box = BoundingBox()
    # box.normals = cube_normals.copy()
    # position = vec3(x, y - 0.5, z - 1)
    # box.vertices = list(map(lambda v: v + position, cube_vertices.copy()))
    # bounding_boxes.append(box)

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

    index_buffer = IndexBuffer()
    index_buffer.draw_type = GL_TRIANGLES
    index_buffer.draw_count = len(indices)
    index_buffer.indices = indices
    asset.index_buffers.append(index_buffer)

    upload(asset)

    add_mvp_uniforms(asset.uniforms)
    add_light_uniforms(asset.uniforms)
    asset.uniforms["u_Color"] = "color"

    model = ModelInstance()
    model.name = "Labyrinth"
    model.asset = asset
    model.bounding_boxes = bounding_boxes
    model.scale = 10
    model.position = vec3(0, -5, 0)
    model.model_matrix = identity()
    scale(model.model_matrix, model.scale)
    translate(model.model_matrix, model.position)
    return model
