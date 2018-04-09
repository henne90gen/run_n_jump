from ctypes import sizeof

import freetype
import numpy as np
from pyglet.gl import *

from math_helper import vec3, vec2
from render_data import RenderData
from shader import Shader


class FontTexture:
    texture_width = 0.0
    texture_height = 0.0
    character_width = 0.0
    character_height = 0.0
    texture_buffer = None


def load_font(font_path: str = "font/RobotoMono-Regular.ttf", size: int = 48) -> FontTexture:
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

    result = FontTexture()
    result.texture_buffer = data
    result.texture_width = data.shape[1]
    result.texture_height = data.shape[0]
    result.character_width = char_width
    result.character_height = char_height
    return result


class TextShader(Shader):
    def __init__(self, text, path_prefix: str = "shaders/"):
        super().__init__(f"{path_prefix}text_vertex.glsl", f"{path_prefix}text_fragment.glsl")

        self.text = text
        self.vertex_count = 0

        self.vertex_array_id = GLuint()
        glGenVertexArrays(1, self.vertex_array_id)

        self.vertex_buffer_id = GLuint()
        glGenBuffers(1, self.vertex_buffer_id)

        self.texture_id = GLuint()
        glGenTextures(1, self.texture_id)

    def upload_data(self, vertices: list, uvs: list, font_texture: FontTexture):
        self.vertex_count = len(vertices) // 2
        vertex_data = []
        for i in range(0, len(vertices), 2):
            vertex_data.append(vertices[i])
            vertex_data.append(vertices[i + 1])
            vertex_data.append(uvs[i])
            vertex_data.append(uvs[i + 1])

        # noinspection PyCallingNonCallable,PyTypeChecker
        vertex_data_gl = (GLfloat * len(vertex_data))(*vertex_data)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        vertex_buffer_size = sizeof(vertex_data_gl)
        glBufferData(GL_ARRAY_BUFFER, vertex_buffer_size, vertex_data_gl, GL_STATIC_DRAW)

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        # noinspection PyCallingNonCallable,PyTypeChecker
        texture_data = (GLubyte * len(font_texture.texture_buffer.flat))(*font_texture.texture_buffer.flatten())
        glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, font_texture.texture_width, font_texture.texture_height, 0, GL_ALPHA,
                     GL_UNSIGNED_BYTE, texture_data)

    def bind(self, render_data: RenderData):
        super().bind()

        glBindVertexArray(self.vertex_array_id)

        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        stride = sizeof(GLfloat) * 4
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, 0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, 2 * sizeof(GLfloat))
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)

        glBindAttribLocation(self.handle, 0, bytes("a_Position", "utf-8"))
        glBindAttribLocation(self.handle, 1, bytes("a_UV", "utf-8"))

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        self.uniformi("u_TextureSampler", 0)

        self.uniformf("u_Offset", *self.text.position)
        self.uniformf("u_Color", *self.text.color)

    def unbind(self):
        glBindVertexArray(0)
        super().unbind()


class Text2D:
    def __init__(self, text: str, position: vec2 = vec2(), color: vec3 = vec3(1.0, 1.0, 1.0), font_size: int = 11):
        self.text = text
        self.color = color
        self.position = position
        self.font_size = font_size

        self.shader = TextShader(self)

        font_texture = load_font(size=font_size)
        vertices, uvs = generate_vertices(text, font_texture)
        self.shader.upload_data(vertices, uvs, font_texture)

    def render(self, render_data: RenderData):
        self.shader.bind(render_data)

        glDrawArrays(GL_TRIANGLES, 0, self.shader.vertex_count)

        self.shader.unbind()


def generate_vertices(text, font_texture: FontTexture):
    vertices = []
    uvs = []

    dx = font_texture.character_width / float(font_texture.texture_width)
    dy = font_texture.character_height / float(font_texture.texture_height)
    current_position = vec2()
    for c in text:
        i = ord(c)
        x = i % 16
        y = i // 16 - 2
        if c == '\n':
            current_position -= vec2(0, font_texture.character_height)
            current_position.x = 0
        elif c == '\t':
            current_position += vec2(4 * font_texture.character_width)
        elif i >= 32:
            vertices.extend([current_position.x, current_position.y])
            vertices.extend([current_position.x + font_texture.character_width, current_position.y])
            vertices.extend(
                [current_position.x + font_texture.character_width, current_position.y + font_texture.character_height])

            uvs.extend([(x) * dx, (y + 1) * dy])
            uvs.extend([(x + 1) * dx, (y + 1) * dy])
            uvs.extend([(x + 1) * dx, (y) * dy])

            vertices.extend([current_position.x, current_position.y])
            vertices.extend(
                [current_position.x + font_texture.character_width, current_position.y + font_texture.character_height])
            vertices.extend([current_position.x, current_position.y + font_texture.character_height])

            uvs.extend([(x) * dx, (y + 1) * dy])
            uvs.extend([(x + 1) * dx, (y) * dy])
            uvs.extend([(x) * dx, (y) * dy])

            current_position += vec2(font_texture.character_width)

    return vertices, uvs


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
