import logging
from builtins import bytes
from ctypes import (
    byref, c_char, c_char_p, c_int, c_float, cast, create_string_buffer, pointer,
    POINTER, addressof
)

from pyglet.gl import *

import run_n_jump.logging_config as logging_config
from .math_helper import mat4, vec3, vec2

NUMBER_OF_LIGHTS_PLACEHOLDER = "LIGHTS"


class Shader:
    def __init__(self, vertex_shader_name: str = "", fragment_shader_name: str = "", number_of_lights: int = 2):
        self.log = logging_config.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        self.handle = None
        self.linked = False
        self.vertex_shader_name = vertex_shader_name
        self.fragment_shader_name = fragment_shader_name

        self.number_of_lights = number_of_lights
        self.compile(number_of_lights)

    def compile(self, number_of_lights: int):
        self.number_of_lights = number_of_lights

        if self.handle is not None:
            glDeleteProgram(self.handle)
        self.handle = glCreateProgram()

        if len(self.vertex_shader_name) > 0:
            with open(self.vertex_shader_name, "r") as f:
                vertex_source = f.readlines()
            self.create_shader(vertex_source, GL_VERTEX_SHADER)

        if len(self.fragment_shader_name) > 0:
            with open(self.fragment_shader_name, "r") as f:
                fragment_source = f.readlines()
            self.create_shader(fragment_source, GL_FRAGMENT_SHADER)

        self.link()

    def create_shader(self, strings, t):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return

        # create the shader handle
        shader = glCreateShader(t)

        # convert the source strings into a ctypes pointer-to-char array, and upload them
        string_buffers = [self.process_and_convert_to_string_buffer(s) for s in strings]

        # noinspection PyTypeChecker, PyCallingNonCallable
        src = (c_char_p * count)(*map(addressof, string_buffers))
        glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)

        # compile the shader
        glCompileShader(shader)

        temp = c_int(0)
        # retrieve the compile status
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))
        # if compilation failed, print the log
        if not temp:
            # retrieve the log length
            glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
            # create a buffer for the log
            buffer = create_string_buffer(temp.value)
            # retrieve the log text
            glGetShaderInfoLog(shader, temp, None, buffer)
            # print the log to the console
            self.log.error(f"{buffer.value}")
        else:
            # all is well, so attach the shader to the program
            glAttachShader(self.handle, shader)

    def link(self):
        # link the program
        glLinkProgram(self.handle)
        temp = c_int(0)
        # retrieve the link status
        glGetProgramiv(self.handle, GL_LINK_STATUS, byref(temp))
        # if linking failed, print the log
        if not temp:
            # retrieve the log length
            glGetProgramiv(self.handle, GL_INFO_LOG_LENGTH, byref(temp))
            # create a buffer for the log
            buffer = create_string_buffer(temp.value)
            # retrieve the log text
            glGetProgramInfoLog(self.handle, temp, None, buffer)
            # print the log to the console
            self.log.error(f"{buffer.value}")
        else:
            # all is well, so we are linked
            self.linked = True

    def bind(self, *args):
        # bind the program
        glUseProgram(self.handle)

    def unbind(self):
        # unbind whatever program is currently bound - not necessarily this program,
        # so this should probably be a class method instead
        glUseProgram(0)

    def uniform(self, name: str, data, index: int = -1):
        if index > -1:
            name = f"{name}[{index}]"

        self.log.debug(f"Binding {name} with data: {data}")

        data_type = type(data)
        if data_type == mat4:
            self.uniform_matrixf(name, data)

        elif data_type in [vec2, vec3]:
            self.uniformf(name, *data)

        elif data_type == float:
            self.uniformf(name, data)

        elif data_type == int:
            self.uniformi(name, data)

        elif data_type == list:
            for index, d in enumerate(data):
                self.uniform(name, d, index)

        elif data_type == dict:
            for key in data:
                self.uniform(f"{name}.{key}", data[key])

        else:
            self.log.error(f"Could not bind {name}")
            return
        self.log.debug(f"Bound {name} with data: {data}")

    def uniformf(self, name: str, *vals):
        # upload a floating point uniform
        # this program must be currently bound
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            vals = list(map(c_float, vals))
            location = glGetUniformLocation(self.handle, c_char_p(name.encode("utf-8")))
            # select the correct function
            uniform_functions = {1: glUniform1f, 2: glUniform2f, 3: glUniform3f, 4: glUniform4f}
            uniform_functions[len(vals)](location, *vals)

    def uniformi(self, name: str, *vals):
        # upload an integer uniform
        # this program must be currently bound
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            vals = list(map(c_int, vals))
            # select the correct function
            location = glGetUniformLocation(self.handle, c_char_p(name.encode("utf-8")))
            uniform_functions = {1: glUniform1i, 2: glUniform2i, 3: glUniform3i, 4: glUniform4i}
            uniform_functions[len(vals)](location, *vals)

    def uniform_matrixf(self, name: str, mat: mat4):
        # upload a uniform matrix
        # works with matrices stored as lists,
        # as well as euclid matrices
        # obtain the uniform location
        location = glGetUniformLocation(self.handle, c_char_p(name.encode("utf-8")))
        # upload the 4x4 floating point matrix
        mat_values = mat.to_list()
        # noinspection PyCallingNonCallable, PyTypeChecker
        glUniformMatrix4fv(location, 1, True, (c_float * 16)(*mat_values))

    def process_and_convert_to_string_buffer(self, s: str):
        if NUMBER_OF_LIGHTS_PLACEHOLDER in s:
            s = s.replace(NUMBER_OF_LIGHTS_PLACEHOLDER, str(self.number_of_lights))
        return create_string_buffer(bytes(s, "utf-8"))
