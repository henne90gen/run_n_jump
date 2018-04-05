import math
import random
from datetime import datetime

import numpy as np


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
        if type(other) != float:
            raise AttributeError
        return vec2(self.x * other, self.y * other)

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
            raise AttributeError
        return vec3(self.x * other, self.y * other, self.z * other)

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

    @property
    def length(self) -> float:
        return np.linalg.norm(self.to_list())

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
        return f"\n{self.numbers[0]}\n{self.numbers[1]}\n{self.numbers[2]}\n{self.numbers[3]}\n"

    def __repr__(self):
        return self.__str__()

    def __mul__(self, other):
        if type(other) == mat4:
            return mat4(list(np.matmul(self.numbers, other.numbers)))
        elif type(other) == vec3:
            res = list(np.matmul(self.numbers, [other.x, other.y, other.z, 1]))
            return vec3(arr=res[:-1])
        else:
            raise AttributeError

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


gradient = []
gradient_x = 100
gradient_y = 100
for g_y in range(gradient_y):
    gradient.append([])
    for g_x in range(gradient_x):
        angle = random.random() * 2 * math.pi
        rand_x = math.cos(angle)
        rand_y = math.sin(angle)
        gradient[g_y].append(vec2(rand_x, rand_y))


# Function to linearly interpolate between a0 and a1
# Weight w should be in the range[0.0, 1.0]
def lerp(a0: float, a1: float, w: float):
    return (1.0 - w) * a0 + w * a1


# Computes the dot product of the distance and gradient vectors.
def dotGridGradient(ix: int, iy: int, x: float, y: float):
    # Compute the distance vector
    dx = x - float(ix)
    dy = y - float(iy)

    # Compute the dot - product
    return dx * gradient[iy % gradient_y][ix % gradient_x].x + dy * gradient[iy % gradient_y][ix % gradient_x].y


# Compute Perlin noise at coordinates x, y
def perlin(x: float, y: float):
    # Determine grid cell coordinates
    x0 = int(math.floor(x))
    x1 = x0 + 1
    y0 = int(math.floor(y))
    y1 = y0 + 1

    # Determine interpolation weights
    # Could also use higher order polynomial / s - curve here
    sx = x - float(x0)
    sy = y - float(y0)

    # Interpolate between grid point gradients
    n0 = dotGridGradient(x0, y0, x, y)
    n1 = dotGridGradient(x1, y0, x, y)
    ix0 = lerp(n0, n1, sx)
    n0 = dotGridGradient(x0, y1, x, y)
    n1 = dotGridGradient(x1, y1, x, y)
    ix1 = lerp(n0, n1, sx)
    value = lerp(ix0, ix1, sy)

    return value
