from math_helper import vec3, vec2, identity


class Camera:
    def __init__(self, position: vec3 = vec3(), angle: vec2 = vec2()):
        self.model_matrix = identity()
        self.position = position
        self.rotation = vec3(angle.x, angle.y, 0)
        self.velocity = vec3()
        self.acceleration = vec3()
        self.player = True
        self.speed = 0.5
        self.max_speed = 0.15
