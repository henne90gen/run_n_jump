from math_helper import identity, vec3


class RenderData:
    frame_time = 0.0
    view_matrix = identity()
    projection_matrix = identity()
    light_position = vec3()
    light_direction = vec3()
