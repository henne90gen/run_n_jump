from ctypes import sizeof, c_float

import freetype
import numpy as np
from pyglet.gl import *

from math_helper import vec3, vec2, identity
from model import ModelAsset, upload, ModelInstance, Texture, add_texture_uniform, IndexBuffer, \
    upload_vertices, upload_indices
from shader import Shader


def load_font(font_path: str = "font/RobotoMono-Regular.ttf", size: int = 48) -> Texture:
    # Load font
    face = freetype.Face(font_path)
    face.set_char_size(size * 64)

    # Determine largest glyph size
    char_width, char_height, ascender, descender = 0, 0, 0, 0
    for c in range(32, 128):
        face.load_char(chr(c), freetype.FT_LOAD_RENDER | freetype.FT_LOAD_FORCE_AUTOHINT)
        bitmap = face.glyph.bitmap
        char_width = max(char_width, bitmap.width)
        ascender = max(ascender, face.glyph.bitmap_top)
        descender = max(descender, bitmap.rows - face.glyph.bitmap_top)
    char_height = ascender + descender

    # Generate texture data
    data = np.zeros((char_height * 6, char_width * 16), dtype=np.ubyte)
    for j in range(6):
        for i in range(16):
            face.load_char(chr(32 + j * 16 + i), freetype.FT_LOAD_RENDER | freetype.FT_LOAD_FORCE_AUTOHINT)
            bitmap = face.glyph.bitmap
            x = i * char_width + face.glyph.bitmap_left
            y = j * char_height + ascender - face.glyph.bitmap_top

            data[y:y + bitmap.rows, x:x + bitmap.width].flat = bitmap.buffer

    result = Texture()
    result.buffer = data
    result.width = data.shape[1]
    result.height = data.shape[0]
    result.attributes["character_width"] = char_width
    result.attributes["character_height"] = char_height
    result.format = GL_ALPHA
    result.type = GL_UNSIGNED_BYTE
    return result


def generate_vertices(text: str, font_texture: Texture):
    if type(text) != str:
        text = str(text)

    vertices = []
    uvs = []

    character_width = font_texture.attributes["character_width"]
    character_height = font_texture.attributes["character_height"]

    dx = character_width / float(font_texture.width)
    dy = character_height / float(font_texture.height)
    current_position = vec2()
    for c in text:
        i = ord(c)
        x = i % 16
        y = i // 16 - 2
        if c == '\n':
            current_position -= vec2(0, character_height)
            current_position.x = 0
        elif c == '\t':
            current_position += vec2(4 * character_width)
        elif i >= 32:
            vertices.extend([current_position.x, current_position.y])
            vertices.extend([current_position.x + character_width, current_position.y])
            vertices.extend(
                [current_position.x + character_width, current_position.y + character_height])

            uvs.extend([(x) * dx, (y + 1) * dy])
            uvs.extend([(x + 1) * dx, (y + 1) * dy])
            uvs.extend([(x + 1) * dx, (y) * dy])

            vertices.extend([current_position.x, current_position.y])
            vertices.extend(
                [current_position.x + character_width, current_position.y + character_height])
            vertices.extend([current_position.x, current_position.y + character_height])

            uvs.extend([(x) * dx, (y + 1) * dy])
            uvs.extend([(x + 1) * dx, (y) * dy])
            uvs.extend([(x) * dx, (y) * dy])

            current_position += vec2(character_width)

    return vertices, uvs


def text2d(text: str, position: vec2 = vec2(), color: vec3 = vec3(1.0, 1.0, 1.0), font_size: int = 11):
    asset = ModelAsset()
    asset.shader = Shader("shaders/text_vertex.glsl", "shaders/text_fragment.glsl")
    stride = 4 * sizeof(c_float)
    attributes = [
        (0, 'a_Position', GL_FLOAT, 2, stride, 0),
        (1, 'a_UV', GL_FLOAT, 2, stride, 2 * sizeof(c_float))
    ]
    asset.attributes = attributes

    font_texture = load_font(size=font_size)
    font_texture.texture_unit = GL_TEXTURE0
    asset.texture = font_texture
    index_buffer = IndexBuffer()
    asset.index_buffers.append(index_buffer)

    add_texture_uniform(asset.uniforms)

    asset.uniforms["u_Model"] = "model_matrix"
    asset.uniforms["u_Offset"] = "position"
    asset.uniforms["u_Color"] = "color"

    upload(asset, GL_DYNAMIC_DRAW)

    model = ModelInstance()
    model.model_matrix = identity()
    model.asset = asset
    model.color = color
    model.position = vec3(*position, 0)
    model.name = "Text(" + text.replace("\n", " ").replace("\t", "") + ")"
    model.text = text

    update_text(model, text)
    return model


def update_text(model: ModelInstance, new_text: str):
    vertices, uvs = generate_vertices(new_text, model.asset.texture)
    model.asset.attribute_data = {'vertices': (2, vertices), 'uvs': (2, uvs)}

    model.asset.index_buffers[0].draw_type = GL_TRIANGLES
    model.asset.index_buffers[0].indices = list(range(len(vertices)))
    model.asset.index_buffers[0].draw_count = len(model.asset.index_buffers[0].indices)

    upload_vertices(model.asset, GL_DYNAMIC_DRAW)
    upload_indices(model.asset, GL_DYNAMIC_DRAW)


def generate_vertices_for_whole_font():
    vertices = []
    uvs = []

    size = 600
    vertices.extend([0, 0])
    vertices.extend([size, 0])
    vertices.extend([size, size])
    vertices.extend([0, 0])
    vertices.extend([size, size])
    vertices.extend([0, size])

    texture_size = 1.0
    uvs.extend([0, texture_size])
    uvs.extend([texture_size, texture_size])
    uvs.extend([texture_size, 0])
    uvs.extend([0, texture_size])
    uvs.extend([texture_size, 0])
    uvs.extend([0, 0])

    return vertices, uvs
