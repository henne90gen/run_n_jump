from datetime import datetime
import hot_reload

import pyglet
from pyglet.gl import *

import game
from shader import Shader

MODULE_WHITELIST = ['game']


class Window(pyglet.window.Window):
    def __init__(self, width, height, resizable: bool = False):
        super(Window, self).__init__(width, height, resizable=resizable)

        self.set_exclusive_mouse(True)

        glEnable(GL_DEPTH_TEST)
        glEnable(pyglet.gl.GL_BLEND)
        glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0, 0, 0, 1)

        # glEnable(GL_CULL_FACE)

        self.num_frames = 0
        self.start_time = datetime.now()
        self.frame_start_time = datetime.now()

        self.game = game.Game()

        self.shader = Shader("terrain_vertex.glsl", "terrain_fragment.glsl")

    def show_average_time(self):
        self.num_frames += 1
        end = datetime.now()
        diff = end - self.start_time
        average = diff.total_seconds() * 1000.0 / self.num_frames
        average_string = '%.5f' % average
        self.set_caption("Tower Defense " + str(average_string))

        if diff.total_seconds() > 1:
            self.start_time = end
            self.num_frames = 0

    def on_draw(*args):
        # Hack required for pyglets 'schedule_interval' to work
        self = args[0]

        end = datetime.now()
        frame_time = (end - self.frame_start_time).total_seconds()
        self.frame_start_time = datetime.now()

        hot_reload.reload_all(MODULE_WHITELIST)

        self.clear()
        self.game.tick(frame_time)
        self.show_average_time()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect_ratio = width / height
        gluPerspective(75, aspect_ratio, 1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def on_key_press(self, symbol, modifiers):
        self.game.handle_key_event(symbol, modifiers, True)

    def on_key_release(self, symbol, modifiers):
        self.game.handle_key_event(symbol, modifiers, False)

    def on_mouse_motion(self, x, y, dx, dy):
        self.game.handle_mouse_motion_event(dx, dy)


if __name__ == '__main__':
    window = Window(width=1280, height=720, resizable=True)
    window.set_caption("Tower Defense")

    pyglet.clock.schedule_interval(window.on_draw, 1 / 120.0)
    pyglet.clock.set_fps_limit(120)
    pyglet.app.run()
