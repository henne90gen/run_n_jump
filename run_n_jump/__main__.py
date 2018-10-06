import math
from datetime import datetime

import pyglet
from pyglet.gl import glEnable, GL_DEPTH_TEST, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from pyglet.gl import glClearColor, glViewport

import run_n_jump.game as game
import run_n_jump.hot_reload as hot_reload
from .math_helper import identity, mat4, vec2
from .game_data import GameData

MODULE_WHITELIST = ['game']


class Window(pyglet.window.Window):
    def __init__(self, width, height, resizable: bool = False):
        super(Window, self).__init__(width, height, resizable=resizable)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0, 0, 0, 1)

        # glEnable(GL_CULL_FACE)

        self.num_frames = 0
        self.start_time = datetime.now()
        self.frame_start_time = datetime.now()

        self.projection_matrix = identity()
        self.mouse_position = vec2()
        self.mouse_movement = vec2()
        self.key_map = {}
        self.game = game.Game()
        self.game_data = GameData()

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

    def on_draw(self, *args):
        end = datetime.now()
        frame_time = (end - self.frame_start_time).total_seconds()
        self.frame_start_time = datetime.now()

        # hot_reload.reload_all(MODULE_WHITELIST)

        self.clear()

        self.game_data.frame_time = frame_time
        self.game_data.screen_dimensions = vec2(self.width, self.height)
        self.game_data.projection_matrix = self.projection_matrix
        self.game_data.key_map = self.key_map
        self.game_data.mouse_position = self.mouse_position
        self.game_data.mouse_movement = self.mouse_movement
        self.set_exclusive_mouse(not self.game_data.show_overview)
        show_overview_before = self.game_data.show_overview

        self.game.tick(self.game_data)

        if show_overview_before != self.game_data.show_overview:
            self.on_resize(self.width, self.height)

        # resetting mouse movement after each tick
        self.mouse_movement = vec2()

        self.show_average_time()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

        if self.game_data.show_overview:
            self.orthographic_projection(width, height)
        else:
            self.perspective_projection(width, height)

    def orthographic_projection(self, width, height):
        z_near = 1
        z_far = 500
        temp1 = -2 / (z_far - z_near)
        temp2 = -1 * (z_far + z_near) / (z_far - z_near)
        self.projection_matrix = mat4([
            [2 / width, 0, 0, 0],
            [0, 2 / height, 0, 0],
            [0, 0, temp1, temp2],
            [0, 0, 0, 1],
        ])

    def perspective_projection(self, width, height):
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

    def on_key_release(self, symbol, modifiers):
        self.key_map[symbol] = False
        self.game.handle_key(symbol, modifiers, False)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_movement = vec2(dx, dy)
        self.mouse_position = vec2(x, y)


if __name__ == '__main__':
    window = Window(width=1280, height=720, resizable=True)
    window.set_caption("Run'n'Jump")

    pyglet.clock.schedule_interval(window.on_draw, 1 / 120.0)
    pyglet.clock.set_fps_limit(120)
    pyglet.app.run()
