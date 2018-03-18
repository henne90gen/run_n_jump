from datetime import datetime
import pyglet
import hot_reload

import game


module_whitelist = ['game']

num_frames = 0
start_time = datetime.now()

window = pyglet.window.Window(width=1280, height=720, resizable=True)
window.set_caption("Tower Defense")

g = game.Game()


def handle_key(symbol, modifiers, key_down):
    print("KeyEvent", key_down, symbol, modifiers)


def show_average_time():
    global num_frames, start_time
    num_frames += 1
    end = datetime.now()
    diff = end - start_time
    average = diff.total_seconds() * 1000.0 / num_frames
    average_string = '%.5f' % average
    window.set_caption("Tower Defense " + str(average_string))

    if diff.total_seconds() > 1:
        start_time = end
        num_frames = 0


@window.event
def on_key_press(symbol, modifiers):
    handle_key(symbol, modifiers, True)


@window.event
def on_key_release(symbol, modifiers):
    handle_key(symbol, modifiers, False)


@window.event
def on_mouse_motion(x, y, dx, dy):
    pass


@window.event
def on_mouse_press(x, y, button, modifiers):
    print("MousePress", x, y, button, modifiers)


@window.event
def on_draw(_=None):
    hot_reload.reload_all(whitelist=module_whitelist, debug=False)

    window.clear()

    draw_rect()

    # g.tick()

    # gs.clean_up()

    show_average_time()


def draw_rect():
    back_vertices = [-1, 1, 0,
                     1, 1, 0,
                     1, -1, 0,
                     -1, -1, 0]
    # back_vertices = list(map(lambda x: x * 100, back_vertices))
    # pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    # pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    pyglet.gl.glEnable(pyglet.gl.GL_DEPTH_TEST)
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v3f', back_vertices))


pyglet.clock.schedule_interval(on_draw, 1 / 120.0)
pyglet.clock.set_fps_limit(120)
pyglet.app.run()
