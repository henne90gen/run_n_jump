import pyglet


class vec3:
    def __init__(self, x: int=0, y: int=0, z: int=0):
        self.x = x
        self.y = y
        self.z = z


class Player:
    def __init__(self):
        self.position = vec3()
        self.direction = vec3(1)

    def update(self):
        pass

    def render(self):
        pass


class Cube:
    def __init__(self):
        self.position = vec3()
        self.size = vec3(0.5, 0.5, 0)
        # self.color = vec4()

    def render(self):
        pos = self.position
        s = self.size
        front_vertices = [pos.x + s.x, pos.y + s.y, pos.z + s.z,
                          pos.x + s.x, pos.y - s.y, pos.z + s.z,
                          pos.x - s.x, pos.y - s.y, pos.z + s.z,
                          pos.x - s.x, pos.y + s.y, pos.z + s.z]
        position_group = PositionGroup(pos)
        color = (255, 0, 255)

        # batch = pyglet.graphics.Batch()

        # front_vertices = verts[:4]
        # batch.add(4, pyglet.graphics.GL_QUADS, position_group, ('v3f/static', front_vertices),
        #           ('c3B/static', (*color, *color, *color, *color)))

        back_vertices = [pos.x - s.x, pos.y + s.y, 
                         pos.x + s.x, pos.y + s.y, 
                         pos.x + s.x, pos.y - s.y, 
                         pos.x - s.x, pos.y - s.y, ]
        print(back_vertices)
        # batch.add(4, pyglet.graphics.GL_QUADS, position_group, ('v3f/static', back_vertices), ('c3B/static', (*color, *color, *color, *color)))
        # pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        # pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', back_vertices), ('c3B', (*color, *color, *color, *color)))

        # batch.draw()


class PositionGroup(pyglet.graphics.Group):
    def __init__(self, position: vec3, parent: pyglet.graphics.Group = None):
        super().__init__(parent)
        self.position = position

    def set_state(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(self.position.x, self.position.y, 0)

    def unset_state(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()


class Game:
    def __init__(self):
        self.player = Player()

    def tick(self):
        Cube().render()
