import math
from datetime import datetime

import numpy as np


# noinspection PyPep8Naming
class vec2:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return "vec2(" + str(self.x) + ", " + str(self.y) + ")"

    def __repr__(self):
        return str(self)

    def rotate(self, angle: float):
        angle = (angle * math.pi) / 180
        x = math.cos(angle) * self.x - math.sin(angle) * self.y
        y = math.sin(angle) * self.x + math.cos(angle) * self.y
        self.x = x
        self.y = y
        return self

    def __eq__(self, other):
        if type(other) != vec2:
            raise AttributeError
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if type(other) != vec2:
            raise AttributeError
        return vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if type(other) != vec2:
            raise AttributeError
        return vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if type(other) not in [float, int]:
            raise AttributeError
        return vec2(self.x * other, self.y * other)

    def __truediv__(self, other):
        if type(other) not in [float, int]:
            raise AttributeError
        return vec2(self.x / other, self.y / other)

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

    def to_list(self):
        return [self.x, self.y]

    @property
    def length(self) -> float:
        return np.linalg.norm(self.to_list())

    def normalize(self):
        length = self.length
        self.x /= length
        self.y /= length
        return self


# noinspection PyPep8Naming
class vec3:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, arr=None):
        if arr is not None:
            if len(arr) != 3:
                raise AttributeError(f"Can't construct vec3, wrong size of array: {len(arr)}")
            self.x = arr[0]
            self.y = arr[1]
            self.z = arr[2]
        else:
            self.x = x
            self.y = y
            self.z = z

    def __str__(self):
        return f"vec3({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if type(other) != vec3:
            raise AttributeError
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __add__(self, other):
        if type(other) != vec3:
            raise AttributeError
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if type(other) != vec3:
            raise AttributeError
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if type(other) not in [float, int]:
            raise AttributeError(f"{type(other)} is not float or int")
        return vec3(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        if type(other) not in [float, int]:
            raise AttributeError(f"{type(other)} is not float or int")
        return vec3(self.x / other, self.y / other, self.z / other)

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

    def __hash__(self):
        return int(f"{self.x}{self.y}{self.z}".replace("-", "").replace(".", ""))

    def __len__(self):
        return self.length

    @property
    def length(self) -> float:
        return float(np.linalg.norm(self.to_list()))

    def copy(self):
        return vec3(self.x, self.y, self.z)

    def normalize(self):
        length = self.length
        self.x /= length
        self.y /= length
        self.z /= length
        return self

    def calculate_normal(self, v1, v2):
        edge1 = v1 - self
        edge2 = v2 - self
        return cross(edge1, edge2).normalize()

    def to_list(self) -> list:
        return [self.x, self.y, self.z]

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


def cross(u, v) -> vec3:
    return vec3(arr=np.cross(u.to_list(), v.to_list()))


def dot(u: vec3, v: vec3) -> float:
    return u.x * v.x + u.y * v.y + u.z * v.z


# noinspection PyPep8Naming
class mat4:
    """
    Row-major matrix
    """

    def __init__(self, arr=None):
        if arr is None:
            arr = []
        self.numbers = []
        for r in range(4):
            self.numbers.append([])
            for c in range(4):
                if len(arr) > r and len(arr[r]) > c:
                    num = float(arr[r][c])
                else:
                    num = 0
                self.numbers[r].append(num)

    def __eq__(self, other):
        if type(other) != mat4:
            return False
        for r in range(4):
            for c in range(4):
                if self.numbers[r][c] != other.numbers[r][c]:
                    return False
        return True

    def __str__(self):
        return f"[{self.numbers[0]}, {self.numbers[1]}, {self.numbers[2]}, {self.numbers[3]}]"

    def __repr__(self):
        return self.__str__()

    def __mul__(self, other):
        if type(other) == mat4:
            return mat4(list(np.matmul(self.numbers, other.numbers)))
        elif type(other) == vec3:
            res = list(np.matmul(self.numbers, [other.x, other.y, other.z, 1]))
            return vec3(arr=res[:-1])
        else:
            raise AttributeError(other)

    def copy(self):
        m = mat4()
        m.numbers = self.numbers.copy()
        return m

    def to_list(self, column_major=False):
        res = []
        if column_major:
            for r in range(4):
                for c in range(4):
                    res.append(self.numbers[c][r])
        else:
            for r in range(4):
                for c in range(4):
                    res.append(self.numbers[r][c])
        return res


def identity():
    return mat4([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])


def scale(m: mat4, s):
    if type(s) in [float, int]:
        s = vec3(s, s, s)

    m1 = mat4()
    m1.numbers = m.numbers
    m2 = mat4([
        [s.x, 0, 0, 0],
        [0, s.y, 0, 0],
        [0, 0, s.z, 0],
        [0, 0, 0, 1],
    ])
    res = m2 * m1
    m.numbers = res.numbers


def translate(m: mat4, v: vec3):
    m1 = mat4()
    m1.numbers = m.numbers
    m2 = mat4([
        [1, 0, 0, v.x],
        [0, 1, 0, v.y],
        [0, 0, 1, v.z],
        [0, 0, 0, 1],
    ])
    res = m2 * m1
    m.numbers = res.numbers


def rotate(m: mat4, v: vec3, radians=False):
    if not radians:
        v *= math.pi / 180

    precision = 15
    sin_x = round(math.sin(v.x), precision)
    cos_x = round(math.cos(v.x), precision)
    rot_x = mat4([
        [1, 0, 0, 0],
        [0, cos_x, -sin_x, 0],
        [0, sin_x, cos_x, 0],
        [0, 0, 0, 1]
    ])
    sin_y = round(math.sin(v.y), precision)
    cos_y = round(math.cos(v.y), precision)
    rot_y = mat4([
        [cos_y, 0, sin_y, 0],
        [0, 1, 0, 0],
        [-sin_y, 0, cos_y, 0],
        [0, 0, 0, 1]
    ])
    sin_z = round(math.sin(v.z), precision)
    cos_z = round(math.cos(v.z), precision)
    rot_z = mat4([
        [cos_z, -sin_z, 0, 0],
        [sin_z, cos_z, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    res = rot_x * rot_y * rot_z * m
    m.numbers = res.numbers


class timer:
    def __init__(self):
        self.start = None
        self.end = None

    def __enter__(self):
        self.start = datetime.now()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = datetime.now()
        diff = self.end - self.start
        print(f"This took {diff.total_seconds()} seconds")
