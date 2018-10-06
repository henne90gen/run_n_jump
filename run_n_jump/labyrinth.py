from ctypes import c_float, sizeof

import numpy as np
from PIL import Image
from pyglet.gl import *

from .math_helper import identity, vec3, translate, scale, vec2
from .model import ModelAsset, ModelInstance, upload, add_mvp_uniforms, add_light_uniforms, \
    BoundingBox, IndexBuffer, get_line_indices
from .rectangle import rectangular_prism_vertices
from .shader import Shader

LABYRINTH_SCALE = 5


def load_image(filename: str):
    labyrinth_map = Image.open(filename)
    width = labyrinth_map.width
    height = labyrinth_map.height
    image_array = np.asarray(labyrinth_map).flatten()
    map_array = np.zeros((width, height))
    for row in range(height):
        for col in range(width):
            map_array[row, col] = image_array[row * width + col]
    return map_array


def save_image(arr: np.ndarray, filename: str):
    im = Image.new('L', (arr.shape[1], arr.shape[0]))
    im.putdata(arr.flatten().tolist())
    im.save(f"{filename.split('.')[0]}_gen.png")


def is_edge_pixel(arr: np.ndarray, row: int, col: int):
    return arr[row, col] == 255 and (
            row - 1 < 0 or
            row + 1 >= arr.shape[0] or
            col - 1 < 0 or
            col + 1 >= arr.shape[1] or
            arr[row + 1, col] == 0 or
            arr[row + 1, col + 1] == 0 or
            arr[row + 1, col - 1] == 0 or
            arr[row - 1, col] == 0 or
            arr[row - 1, col + 1] == 0 or
            arr[row - 1, col - 1] == 0 or
            arr[row, col + 1] == 0 or
            arr[row, col - 1] == 0
    )


def mark_edges(arr: np.ndarray):
    for row in range(arr.shape[0]):
        for col in range(arr.shape[1]):
            if is_edge_pixel(arr, row, col):
                arr[row, col] = 128
    return arr


def find_next_black_pixel(arr: np.ndarray, row: int, col: int):
    while True:
        if col < arr.shape[1] - 1:
            col += 1
        elif row < arr.shape[0] - 1:
            row += 1
            col = 0
        else:
            return -1, -1

        if arr[row, col] == 255:
            return row, col


def find_bottom_edge(arr: np.ndarray, start_row: int, col: int):
    for row in range(start_row, arr.shape[0]):
        if arr[row, col] != 255:
            return row - 1
    return arr.shape[0] - 1


def find_right_edge(arr: np.ndarray, used_pixels: list, start_row, end_row, start_col):
    for col in range(start_col, arr.shape[1]):
        for row in range(start_row, end_row + 1):
            if arr[row, col] != 255 or (row, col) in used_pixels:
                return col - 1
    return arr.shape[1] - 1


def add_horizontal_plane(vertices, normals, indices, normal_direction, start: vec2, end: vec2):
    index = len(indices)
    indices.extend([index, index + 1, index + 2, index + 3, index + 4, index + 5])

    normal = [0, normal_direction, 0]
    for _ in range(6):
        normals.extend(normal)

    end += vec2(1, 1)
    normal_direction *= -1
    vertices.extend([start.x, normal_direction, start.y])
    vertices.extend([end.x, normal_direction, start.y])
    vertices.extend([end.x, normal_direction, end.y])

    vertices.extend([start.x, normal_direction, start.y])
    vertices.extend([end.x, normal_direction, end.y])
    vertices.extend([start.x, normal_direction, end.y])


def add_floor(vertices, normals, indices, start, end):
    add_horizontal_plane(vertices, normals, indices, -1, start, end)


def add_ceiling(vertices, normals, indices, start, end):
    add_horizontal_plane(vertices, normals, indices, 1, start, end)


def generate_floor_and_ceiling(arr: np.ndarray, block_offset: vec2, vertices: list, normals: list, indices: list):
    cur_row = 0
    cur_col = -1
    used_pixels = []
    while True:
        cur_row, cur_col = find_next_black_pixel(arr, cur_row, cur_col)
        if (cur_row, cur_col) in used_pixels:
            continue
        if cur_row == -1 or cur_col == -1:
            break
        end_row = find_bottom_edge(arr, cur_row, cur_col)
        end_col = find_right_edge(arr, used_pixels, cur_row, end_row, cur_col)

        add_floor(vertices, normals, indices, vec2(cur_col, cur_row) - block_offset,
                  vec2(end_col, end_row) - block_offset)
        add_ceiling(vertices, normals, indices, vec2(cur_col, cur_row) - block_offset,
                    vec2(end_col, end_row) - block_offset)

        for row in range(cur_row, end_row + 1):
            for col in range(cur_col, end_col + 1):
                used_pixels.append((row, col))


def is_edge(arr, row, col, direction):
    neighbor_row = row + direction[0]
    neighbor_col = col + direction[1]
    return arr[row, col] == 128 and \
           0 < neighbor_row < arr.shape[0] and \
           0 < neighbor_col < arr.shape[1] and \
           arr[neighbor_row, neighbor_col] == 255


def find_next_edge_pixel(arr: np.ndarray, row, col, offset):
    while True:
        if col < arr.shape[1] - 1:
            col += 1
        elif row < arr.shape[0] - 1:
            row += 1
            col = 0
        else:
            return -1, -1

        if is_edge(arr, row, col, offset):
            return row, col


def find_right_end(arr: np.ndarray, row, start_col, direction):
    for col in range(start_col, arr.shape[1]):
        if not is_edge(arr, row, col, (direction, 0)):
            return col
    return arr.shape[1]


def add_vertical_plane_x_y(vertices, normals, indices, normal_direction, row, start_col, end_col):
    index = len(indices)
    indices.extend([index, index + 1, index + 2, index + 3, index + 4, index + 5])

    normal = [0, 0, normal_direction]
    for _ in range(6):
        normals.extend(normal)

    vertices.extend([start_col, -1, row])
    vertices.extend([end_col, -1, row])
    vertices.extend([end_col, 1, row])

    vertices.extend([start_col, -1, row])
    vertices.extend([end_col, 1, row])
    vertices.extend([start_col, 1, row])


def generate_horizontal_wall(arr: np.ndarray, block_offset: vec2, vertices, normals, indices, bounding_boxes,
                             direction):
    cur_row = 0
    cur_col = -1
    used_pixels = []
    while True:
        cur_row, cur_col = find_next_edge_pixel(arr, cur_row, cur_col, (direction, 0))
        if (cur_row, cur_col) in used_pixels:
            continue
        if cur_row == -1 or cur_col == -1:
            break
        end_col = find_right_end(arr, cur_row, cur_col, direction)
        if direction == 1:
            # offset for the back wall
            row = cur_row + 1
        else:
            row = cur_row
        add_vertical_plane_x_y(vertices, normals, indices, direction, row - block_offset.x, cur_col - block_offset.y,
                               end_col - block_offset.y)

        half_width = (end_col - cur_col) / 2
        size = vec3(half_width, 1, 0.5)
        position = vec3(half_width + cur_col - block_offset.y, 0, row - block_offset.x - direction * 0.5)

        if end_col + 1 < arr.shape[1] and arr[row, end_col + 1] != 255:
            size += vec3(0.5, 0, 0)
            position += vec3(0.5, 0, 0)

        if end_col - 1 >= 0 and arr[row, cur_col - 1] != 255:
            size += vec3(0.5, 0, 0)
            position -= vec3(0.5, 0, 0)

        bounding_boxes.append(generate_bounding_box(size, position))

        for col in range(cur_col, end_col):
            used_pixels.append((cur_row, col))


def generate_front(arr, block_offset, vertices, normals, indices, bounding_boxes):
    generate_horizontal_wall(arr, block_offset, vertices, normals, indices, bounding_boxes, 1)


def generate_back(arr, block_offset, vertices, normals, indices, bounding_boxes):
    generate_horizontal_wall(arr, block_offset, vertices, normals, indices, bounding_boxes, -1)


def find_bottom_end(arr: np.ndarray, start_row, col, direction):
    for row in range(start_row, arr.shape[0]):
        if not is_edge(arr, row, col, (0, direction)):
            return row
    return arr.shape[0]


def add_vertical_plane_z_y(vertices, normals, indices, normal_direction, start_row, end_row, col):
    index = len(indices)
    indices.extend([index, index + 1, index + 2, index + 3, index + 4, index + 5])

    normal = [normal_direction, 0, 0]
    for _ in range(6):
        normals.extend(normal)

    vertices.extend([col, -1, start_row])
    vertices.extend([col, -1, end_row])
    vertices.extend([col, 1, end_row])

    vertices.extend([col, -1, start_row])
    vertices.extend([col, 1, end_row])
    vertices.extend([col, 1, start_row])


def generate_vertical_wall(arr: np.ndarray, block_offset: vec2, vertices: list, normals: list, indices: list,
                           bounding_boxes: list, direction: int):
    cur_row = 0
    cur_col = -1
    used_pixels = []
    while True:
        cur_row, cur_col = find_next_edge_pixel(arr, cur_row, cur_col, (0, direction))
        if (cur_row, cur_col) in used_pixels:
            continue
        if cur_row == -1 or cur_col == -1:
            break
        end_row = find_bottom_end(arr, cur_row, cur_col, direction)
        if direction == 1:
            # offset for the right wall
            col = cur_col + 1
        else:
            col = cur_col
        add_vertical_plane_z_y(vertices, normals, indices, direction, cur_row - block_offset.x,
                               end_row - block_offset.x, col - block_offset.y)

        half_height = (end_row - cur_row) / 2
        size = vec3(0.5, 1, half_height)
        position = vec3(col - block_offset.y - direction * 0.5, 0, half_height + cur_row - block_offset.x)

        if end_row + 1 < arr.shape[0] and arr[end_row + 1, col] != 255:
            size += vec3(0, 0, 0.5)
            position += vec3(0, 0, 0.5)

        if end_row - 1 >= 0 and arr[cur_row - 1, col] != 255:
            size += vec3(0, 0, 0.5)
            position -= vec3(0, 0, 0.5)

        bounding_box = generate_bounding_box(size, position)
        bounding_boxes.append(bounding_box)

        for row in range(cur_row, end_row):
            used_pixels.append((row, cur_col))


def generate_left(arr, block_offset, vertices, normals, indices, bounding_boxes):
    generate_vertical_wall(arr, block_offset, vertices, normals, indices, bounding_boxes, 1)


def generate_right(arr, block_offset, vertices, normals, indices, bounding_boxes):
    generate_vertical_wall(arr, block_offset, vertices, normals, indices, bounding_boxes, -1)


def generate_bounding_box(size: vec3, position: vec3):
    vertices, normals, indices = rectangular_prism_vertices(size)
    return vertices, normals, indices, position


def create_bounding_box(vertices, normals, indices, position: vec3):
    box = BoundingBox()
    asset = ModelAsset()
    asset.color = vec3(1, 0, 1)
    asset.shader = Shader("shaders/bb_vertex.glsl", "shaders/bb_fragment.glsl")
    asset.current_index_buffer_id = 1
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

    def convert_to_vec3(arr: list):
        result = []
        for i in range(0, len(arr), 3):
            vector = vec3(arr[i], arr[i + 1], arr[i + 2])
            if vector not in result:
                result.append(vector)
        return result

    box.vertices = convert_to_vec3(vertices)
    box.normals = convert_to_vec3(normals)
    box.position = position
    box.radius = max(map(lambda v: v.length, box.vertices))
    box.asset = asset
    return box


def generate_vertices(arr: np.ndarray, block_size: int):
    vertices = []
    normals = []
    indices = []
    bounding_boxes = []

    block_offset = vec2(block_size, block_size) / 2.0

    generate_floor_and_ceiling(arr, block_offset, vertices, normals, indices)

    generate_front(arr, block_offset, vertices, normals, indices, bounding_boxes)
    generate_back(arr, block_offset, vertices, normals, indices, bounding_boxes)

    generate_left(arr, block_offset, vertices, normals, indices, bounding_boxes)
    generate_right(arr, block_offset, vertices, normals, indices, bounding_boxes)

    return vertices, normals, [(GL_TRIANGLES, indices), (GL_LINES, get_line_indices(indices))], bounding_boxes


def labyrinth(block_size: int = 15):
    filename = "labyrinth.png"
    image_array = load_image(filename)
    image_array = mark_edges(image_array)
    save_image(image_array, filename)

    for row in range(0, image_array.shape[1], block_size - 2):
        for col in range(0, image_array.shape[0], block_size - 2):
            block = image_array[row:row + block_size, col:col + block_size]
            vertices, normals, indices, bounding_boxes = generate_vertices(block, block_size)
            if len(vertices) != 0:
                yield row, col, block_size, vertices, normals, indices, bounding_boxes


def create_labyrinth(row_offset: int, col_offset: int, block_size: int, vertices, normals, indices, bounding_boxes):
    asset = ModelAsset()
    asset.shader = Shader("shaders/model_vertex.glsl", "shaders/model_fragment.glsl")
    stride = 6 * sizeof(c_float)
    attributes = [
        (0, 'a_Position', GL_FLOAT, 3, stride, 0),
        (1, 'a_Normal', GL_FLOAT, 3, stride, 3 * sizeof(c_float))
    ]
    asset.attributes = attributes

    if len(vertices) == 0:
        return None
    asset.attribute_data = {'vertices': (3, vertices), 'normals': (3, normals)}

    for draw_type, values in indices:
        index_buffer = IndexBuffer()
        index_buffer.draw_type = draw_type
        index_buffer.draw_count = len(values)
        index_buffer.indices = values
        asset.index_buffers.append(index_buffer)

    add_mvp_uniforms(asset.uniforms)
    add_light_uniforms(asset.uniforms)
    asset.uniforms["u_Color"] = "color"

    upload(asset)

    model = ModelInstance()
    model.asset = asset
    model.bounding_boxes = [create_bounding_box(*item) for item in bounding_boxes]
    model.scale = LABYRINTH_SCALE
    model.position = vec3((col_offset + block_size / 2) * model.scale, 0, (row_offset + block_size / 2) * model.scale)
    model.name = f"Labyrinth {model.position}"
    model.systems = [
        'position',
        'render'
    ]
    model.model_matrix = identity()
    scale(model.model_matrix, model.scale)
    translate(model.model_matrix, model.position)
    return model
