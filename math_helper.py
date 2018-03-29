import math
import random


class vec2:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return "vec2(" + str(self.x) + ", " + str(self.y) + ")"

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
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
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

    def __sub__(self, other):
        if type(other) != vec3:
            raise AttributeError
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if type(other) != float:
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

    @property
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def copy(self):
        return vec3(self.x, self.y, self.z)

    def normalize(self):
        length = self.length
        self.x /= length
        self.y /= length
        self.z /= length

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


gradient = []
gradient_x = 100
gradient_y = 100
for y in range(gradient_y):
    gradient.append([])
    for x in range(gradient_x):
        angle = random.random() * 2 * math.pi
        rand_x = math.cos(angle)
        rand_y = math.sin(angle)
        gradient[y].append(vec2(rand_x, rand_y))


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
