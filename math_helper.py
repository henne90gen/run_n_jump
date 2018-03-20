import math


class vec2:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def rotate(self, angle: float):
        angle = (angle * math.pi) / 180
        x = math.cos(angle) * self.x - math.sin(angle) * self.y
        y = math.sin(angle) * self.x + math.cos(angle) * self.y
        self.x = x
        self.y = y

    def __eq__(self, other):
        if type(other) != vec2:
            raise AttributeError
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if type(other) != vec2:
            raise AttributeError
        return vec2(self.x + other.x, self.y + other.y)

    def __getitem__(self, item):
        if item == 'x' or item == 0:
            return self.x
        elif item == 'y' or item == 1:
            return self.y
        raise IndexError

    def __setitem__(self, key, value):
        if key == 'x' or key == 0:
            self.x = value
        elif key == 'y' or key == 1:
            self.y = value
        else:
            raise IndexError


class vec3:
    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "vec3(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def __eq__(self, other):
        if type(other) != vec3:
            raise AttributeError
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __add__(self, other):
        if type(other) != vec3:
            raise AttributeError
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __getitem__(self, item):
        if item == 'x' or item == 0:
            return self.x
        elif item == 'y' or item == 1:
            return self.y
        elif item == 'z' or item == 2:
            return self.z
        raise IndexError

    def __setitem__(self, key, value):
        if key == 'x' or key == 0:
            self.x = value
        elif key == 'y' or key == 1:
            self.y = value
        elif key == 'z' or key == 2:
            self.z = value
        else:
            raise IndexError

    def to_vec2(self, component_mapping) -> vec2:
        v = vec2()
        t_comp_map = type(component_mapping)
        if t_comp_map == dict:
            for key in component_mapping:
                v[component_mapping[key]] = self[key]
        elif (t_comp_map == list or t_comp_map == tuple) and len(component_mapping) == 2:
            for index, key in enumerate(component_mapping):
                v[index] = self[key]
        else:
            raise AttributeError
        return v
