from pyglet.gl import *

from math_helper import vec3


class identity(pyglet.graphics.Group):
    def __init__(self, parent: pyglet.graphics.Group = None):
        super().__init__(parent)

    def set_state(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


class rotate(pyglet.graphics.Group):
    def __init__(self, rotation: vec3, parent: pyglet.graphics.Group = None):
        super().__init__(parent)
        self.rotation = rotation

    def set_state(self):
        glMatrixMode(GL_MODELVIEW)
        glRotatef(self.rotation.x, 1, 0, 0)
        glRotatef(self.rotation.y, 0, 1, 0)
        glRotatef(self.rotation.z, 0, 0, 1)

    def unset_state(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


class translate(pyglet.graphics.Group):
    def __init__(self, position: vec3, parent: pyglet.graphics.Group = None):
        super().__init__(parent)
        self.position = position

    def set_state(self):
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(self.position.x, self.position.y, self.position.z)

    def unset_state(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
