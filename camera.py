from math_helper import vec3, vec2, identity
from model import BoundingBox


def camera_bounding_box():
    box = BoundingBox()
    box.vertices = [
        vec3(1.0, -1.0, -1.0), vec3(1.0, -1.0, 1.0), vec3(-1.0, -1.0, 1.0), vec3(-1.0, -1.0, -1.0),
        vec3(1.0, 1.0, -1.0), vec3(1.0, 1.0, 1.0), vec3(-1.0, 1.0, 1.0), vec3(-1.0, 1.0, -1.0)
    ]
    box.normals = [vec3(1.0), vec3(0.0, 1.0), vec3(0.0, 0.0, 1.0)]
    box.type = 'dynamic'
    box.radius = max(map(lambda v: v.length, box.vertices))
    return box


class Camera:
    def __init__(self, position: vec3 = vec3(), angle: vec2 = vec2()):
        self.model_matrix = identity()
        self.position = position
        self.rotation = vec3(angle.x, angle.y, 0)
        self.scale = 1
        self.velocity = vec3()
        self.acceleration = vec3()
        self.player = True
        self.speed = 1
        self.max_speed = 0.25
        self.bounding_boxes = [camera_bounding_box()]
        self.systems = [
            'input',
            'movement_input',
            'collision',
            'acceleration',
            'position',
            'render'
        ]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "PlayerCamera"
