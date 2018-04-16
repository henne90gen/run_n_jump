import math
from datetime import datetime

import pyglet
from pyglet.gl import *

import game
import hot_reload
from math_helper import identity, mat4, vec2
from game_data import GameData

MODULE_WHITELIST = ['game']


class Window(pyglet.window.Window):
    def __init__(self, width, height, resizable: bool = False):
        super(Window, self).__init__(width, height, resizable=resizable)

        # self.set_exclusive_mouse(True)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0, 0, 0, 1)

        # glEnable(GL_CULL_FACE)

        self.num_frames = 0
        self.start_time = datetime.now()
        self.frame_start_time = datetime.now()

        self.projection_matrix = identity()
        self.mouse_movement = vec2()
        self.key_map = {}
        self.game = game.Game()

    def show_average_time(self):
        self.num_frames += 1
        end = datetime.now()
        diff = end - self.start_time
        average = diff.total_seconds() * 1000.0 / self.num_frames
        average_string = '%.5f' % average
        self.set_caption("Run'n'Jump " + str(average_string))

        if diff.total_seconds() > 1:
            self.start_time = end
            self.num_frames = 0

    # noinspection PyMethodOverriding
    def on_draw(self, *args):
        end = datetime.now()
        frame_time = (end - self.frame_start_time).total_seconds()
        self.frame_start_time = datetime.now()

        hot_reload.reload_all(MODULE_WHITELIST)

        self.clear()

        game_data = GameData()
        game_data.frame_time = frame_time
        game_data.screen_dimensions = vec2(self.width, self.height)
        game_data.projection_matrix = self.projection_matrix
        game_data.key_map = self.key_map
        game_data.mouse_movement = self.mouse_movement
        self.game.tick(game_data)

        # resetting mouse movement after each tick
        self.mouse_movement = vec2()

        self.show_average_time()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

        aspect_ratio = width / height
        fovy = 75
        z_near = 1
        z_far = 1000
        f = 1 / (math.tan(fovy * math.pi / 360))
        temp1 = (z_far + z_near) / (z_near - z_far)
        temp2 = (2 * z_far * z_near) / (z_near - z_far)
        self.projection_matrix = mat4([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, temp1, temp2],
            [0, 0, -1, 0],
        ])

    def on_key_press(self, symbol, modifiers):
        self.key_map[symbol] = True
        self.game.handle_key(symbol, modifiers, True)

    # noinspection PyMethodOverriding
    def on_key_release(self, symbol, modifiers):
        self.key_map[symbol] = False
        self.game.handle_key(symbol, modifiers, False)

    # noinspection PyMethodOverriding
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_movement = vec2(dx, dy)


if __name__ == '__main__':
    window = Window(width=1280, height=720, resizable=True)
    window.set_caption("Run'n'Jump")

    pyglet.clock.schedule_interval(window.on_draw, 1 / 120.0)
    pyglet.clock.set_fps_limit(120)
    pyglet.app.run()
