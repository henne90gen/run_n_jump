from builtins import bytes
from ctypes import (
    byref, c_char, c_char_p, c_int, c_float, cast, create_string_buffer, pointer,
    POINTER, addressof
)

from pyglet.gl import *

from math_helper import mat4


class Shader:
    def __init__(self, vertex_shader_name: str = "", fragment_shader_name: str = ""):
        # create the program handle
        self.handle = glCreateProgram()
        # we are not linked yet
        self.linked = False

        if len(vertex_shader_name) > 0:
            with open(vertex_shader_name, "r") as f:
                vertex_source = f.readlines()
            self.create_shader(vertex_source, GL_VERTEX_SHADER)

        if len(fragment_shader_name) > 0:
            with open(fragment_shader_name, "r") as f:
                fragment_source = f.readlines()
            self.create_shader(fragment_source, GL_FRAGMENT_SHADER)

        # attempt to link the program
        self.link()

    def create_shader(self, strings, t):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return

        # create the shader handle
        shader = glCreateShader(t)

        # convert the source strings into a ctypes pointer-to-char array, and upload them
        string_buffers = [create_string_buffer(bytes(s, "utf-8")) for s in strings]

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
            print(buffer.value)
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
            print(buffer.value)
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
