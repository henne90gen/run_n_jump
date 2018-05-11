from typing import List

from math_helper import vec2, vec3


class QuadTree:
    position: vec2 = None
    size_half: vec2 = None
    entities: list = None

    def __init__(self, position: vec2, size: vec2, max_entities: int = 5):
        self.position = position
        self.size_half = size / 2
        self.entities = []
        self.quad_trees: List[QuadTree] = []
        self.max_entities = max_entities

    def __str__(self):
        return f"QuadTree[{self.position.x-self.size_half.x}, {self.position.y-self.size_half.y} : {self.position.x+self.size_half.x}, {self.position.y+self.size_half.y}]"

    def __repr__(self):
        return self.__str__()

    def is_in_tree(self, position):
        pos = vec2(position.x, position.z)
        if self.position.x - self.size_half.x < pos.x <= self.position.x + self.size_half.x:
            if self.position.y - self.size_half.y < pos.y <= self.position.y + self.size_half.y:
                return True
        return False

    def create_sub_trees(self):
        result = []

        size_quarter = self.size_half / 2

        top_left = self.position + vec2(-size_quarter.x, size_quarter.y)
        result.append(QuadTree(top_left, self.size_half, self.max_entities))

        top_right = self.position + vec2(size_quarter.x, size_quarter.y)
        result.append(QuadTree(top_right, self.size_half, self.max_entities))

        bottom_left = self.position + vec2(-size_quarter.x, -size_quarter.y)
        result.append(QuadTree(bottom_left, self.size_half, self.max_entities))

        bottom_right = self.position + vec2(size_quarter.x, -size_quarter.y)
        result.append(QuadTree(bottom_right, self.size_half, self.max_entities))

        return result

    def add(self, entity):
        if not self.is_in_tree(entity.position):
            return

        if len(self.quad_trees) == 0:
            if len(self.entities) < self.max_entities:
                self.entities.append(entity)
            else:
                self.quad_trees.extend(self.create_sub_trees())

                for tree in self.quad_trees:
                    tree.add(entity)
                    for e in self.entities:
                        tree.add(e)

                self.entities = []
        else:
            for tree in self.quad_trees:
                tree.add(entity)

    def overlaps_tree(self, position: vec3, rectangle: vec2):
        top_right = vec2(self.position.x + self.size_half.x, self.position.y + self.size_half.x)
        bottom_left = vec2(self.position.x - self.size_half.x, self.position.y - self.size_half.x)
        other_top_right = vec2(position.x + rectangle.x / 2, position.z + rectangle.y / 2)
        other_bottom_left = vec2(position.x - rectangle.x / 2, position.z - rectangle.y / 2)

        return not (
                top_right.x < other_bottom_left.x or
                bottom_left.x > other_top_right.x or
                top_right.y < other_bottom_left.y or
                bottom_left.y > other_top_right.y
        )

    def query(self, position: vec3, rectangle: vec2 = vec2(100, 100)):
        if not self.overlaps_tree(position, rectangle):
            return []

        if len(self.quad_trees) == 0:
            return self.entities
        else:
            result = []
            for tree in self.quad_trees:
                tree_result = tree.query(position, rectangle)
                if tree_result is not None:
                    result.extend(tree_result)
            return result


def get_indentation(indentation):
    text = ""
    for i in range(indentation):
        text += "\t"
    return text


def print_quad_tree(tree: QuadTree, indentation: int = 0):
    text = get_indentation(indentation)
    text += str(tree) + "\n"

    for entity in tree.entities:
        indent = get_indentation(indentation + 1)
        text += indent + str(entity) + "\n"

    for t in tree.quad_trees:
        text += print_quad_tree(t, indentation + 1)
        if not text.endswith("\n"):
            text += "\n"

    return text
