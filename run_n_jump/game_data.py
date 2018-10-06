from .camera import Camera
from .math_helper import identity, vec3, vec2
from .quad_tree import QuadTree


class GameData:
    frame_time = 0.0

    key_map = {}
    mouse_position = vec2()
    mouse_movement = vec2()

    screen_dimensions = vec2()

    model_matrix = identity()
    view_matrix = identity()
    projection_matrix = identity()

    lights = []
    light_direction = vec3()

    sensitivity = 0.5

    entities: QuadTree = None
    systems = {}

    show_overview = False
    wireframe = False
    collision_boxes = False

    camera: Camera = None
    player_configuration = ()

    debug_data = {}
