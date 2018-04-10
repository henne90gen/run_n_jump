import numpy as np
from PIL import Image
from pyglet.gl import *

from math_helper import vec3
from model import Model
from render_data import RenderData


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


class Labyrinth:
    def __init__(self, filename: str = "labyrinth.png"):
        image_array = load_image(filename)
        vertices, normals, indices = generate_vertices(image_array)

        self.model = Model()
        self.model.position = vec3(0, -5, 0)
        self.model.shader.upload_data(vertices, normals, indices, vec3(1.0, 1.0, 1.0))

    def render(self, render_data: RenderData):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.model.render(render_data)


def generate_vertices(arr: np.ndarray):
    vertices = []
    normals = []
    indices = []

    def add_quad_to_index():
        index = len(indices)
        indices.extend([index, index + 1, index + 2, index + 3, index + 4, index + 5])

    def plane(x: float, y: float, normal_direction: float, position: float, scale: float):
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
                plane(col, row, -1, 10, s)
                plane(col, row, 1, 0, s)

                if arr[row + 1, col] != 255:
                    front(col, 0, row + 1, s, -1)
                if arr[row - 1, col] != 255:
                    front(col, 0, row, s, 1)

                if arr[row, col - 1] != 255:
                    left(col, 0, row, s, 1)
                if arr[row, col + 1] != 255:
                    left(col + 1, 0, row, s, -1)

    return vertices, normals, indices
