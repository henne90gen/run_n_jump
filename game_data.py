from math_helper import identity, vec3, vec2


class GameData:
    frame_time = 0.0

    key_map = {}
    mouse_movement = vec2()

    screen_dimensions = vec2()

    model_matrix = identity()
    view_matrix = identity()
    projection_matrix = identity()

    light_position = vec3()
    light_direction = vec3()

    sensitivity = 0.5

    entities = []
