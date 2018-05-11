import unittest

from math_helper import vec2, vec3
from quad_tree import QuadTree, print_quad_tree


class Object:
    position = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Object[{self.position}]"


class QuadTreeTest(unittest.TestCase):
    def test_is_in_tree(self):
        quad_tree = QuadTree(vec2(), vec2(10, 10))
        self.assertTrue(quad_tree.is_in_tree(vec3()))
        self.assertTrue(quad_tree.is_in_tree(vec3(5, 0, 5)))
        self.assertTrue(quad_tree.is_in_tree(vec3(5)))
        self.assertTrue(quad_tree.is_in_tree(vec3(0, 0, 5)))
        self.assertFalse(quad_tree.is_in_tree(vec3(-5, 0, -5)))
        self.assertFalse(quad_tree.is_in_tree(vec3(-5)))
        self.assertFalse(quad_tree.is_in_tree(vec3(0, 0, -5)))

        quad_tree = QuadTree(vec2(10, 10), vec2(5, 5))
        self.assertTrue(quad_tree.is_in_tree(vec3(12.5, 0, 12.5)))
        self.assertTrue(quad_tree.is_in_tree(vec3(12.5, 0, 10)))
        self.assertTrue(quad_tree.is_in_tree(vec3(10, 0, 12.5)))
        self.assertFalse(quad_tree.is_in_tree(vec3(7.5, 0, 7.5)))
        self.assertFalse(quad_tree.is_in_tree(vec3(7.5, 0, 10)))
        self.assertFalse(quad_tree.is_in_tree(vec3(10, 0, 7.5)))

    def test_print(self):
        quad_tree = QuadTree(vec2(), vec2(10, 10))
        entity = Object()
        entity.position = vec3(5, 0, 5)
        quad_tree.entities.append(entity)

        size_quarter = quad_tree.size_half / 2
        top_left = quad_tree.position + vec2(-size_quarter.x, size_quarter.y)
        quad_tree.quad_trees.append(QuadTree(top_left, quad_tree.size_half, quad_tree.max_entities))

        top_right = quad_tree.position + vec2(size_quarter.x, size_quarter.y)
        quad_tree.quad_trees.append(QuadTree(top_right, quad_tree.size_half, quad_tree.max_entities))

        bottom_left = quad_tree.position + vec2(-size_quarter.x, -size_quarter.y)
        quad_tree.quad_trees.append(QuadTree(bottom_left, quad_tree.size_half, quad_tree.max_entities))

        bottom_right = quad_tree.position + vec2(size_quarter.x, -size_quarter.y)
        quad_tree.quad_trees.append(QuadTree(bottom_right, quad_tree.size_half, quad_tree.max_entities))

        actual = print_quad_tree(quad_tree)
        self.assertEqual(
            "QuadTree[-5.0, -5.0 : 5.0, 5.0]\n\tObject[vec3(5, 0, 5)]\n\tQuadTree[-5.0, 0.0 : 0.0, 5.0]\n\t"
            "QuadTree[0.0, 0.0 : 5.0, 5.0]\n\tQuadTree[-5.0, -5.0 : 0.0, 0.0]\n\tQuadTree[0.0, -5.0 : 5.0, 0.0]\n",
            actual)

    def test_query(self):
        quad_tree = QuadTree(vec2(), vec2(10, 10), 2)
        entity1 = Object()
        entity1.position = vec3(5, 0, 5)
        quad_tree.add(entity1)
        actual = quad_tree.query(vec3())
        self.assertEqual(entity1, actual[0])

        entity2 = Object()
        entity2.position = vec3(5)
        quad_tree.add(entity2)
        actual = quad_tree.query(vec3())
        self.assertEqual(entity1, actual[0])
        self.assertEqual(entity2, actual[1])

        actual = quad_tree.query(vec3(5.1))
        self.assertIsNone(actual)

    def test_query_recursion(self):
        quad_tree = QuadTree(vec2(), vec2(10, 10), 2)
        entity1 = Object()
        entity1.position = vec3(2, 0, 1)
        quad_tree.add(entity1)

        entity2 = Object()
        entity2.position = vec3(1, 0, 4)
        quad_tree.add(entity2)

        entity3 = Object()
        entity3.position = vec3(-1, 0, -1)
        quad_tree.add(entity3)

        actual = quad_tree.query(vec3(2, 0, 2))
        expected = [entity1, entity2]
        self.assertEqual(actual, expected)

    def test_add(self):
        root = QuadTree(vec2(), vec2(10, 10), 2)

        entity1 = Object()
        entity1.position = vec3(2, 0, 1)
        root.add(entity1)
        self.assertEqual(1, len(root.entities))

        entity2 = Object()
        entity2.position = vec3(1, 0, 4)
        root.add(entity2)
        self.assertEqual(2, len(root.entities))

        entity3 = Object()
        entity3.position = vec3(-1, 0, -1)
        root.add(entity3)
        self.assertEqual(0, len(root.entities))
        self.assertEqual(4, len(root.quad_trees))

        self.assertEqual(0, len(root.quad_trees[0].entities))
        self.assertEqual(2, len(root.quad_trees[1].entities))
        self.assertEqual(1, len(root.quad_trees[2].entities))
        self.assertEqual(0, len(root.quad_trees[3].entities))

        self.assertEqual(entity1, root.quad_trees[1].entities[0])
        self.assertEqual(entity2, root.quad_trees[1].entities[1])
        self.assertEqual(entity3, root.quad_trees[2].entities[0])

    def test_create_sub_trees(self):
        quad_tree = QuadTree(vec2(), vec2(10, 10), 2)
        sub_trees = quad_tree.create_sub_trees()
        self.assertEqual(4, len(sub_trees))
        size = vec2(2.5, 2.5)
        self.assert_quad_tree(sub_trees[0], vec2(-2.5, 2.5), size)
        self.assert_quad_tree(sub_trees[1], vec2(2.5, 2.5), size)
        self.assert_quad_tree(sub_trees[2], vec2(-2.5, -2.5), size)
        self.assert_quad_tree(sub_trees[3], vec2(2.5, -2.5), size)

        sub_trees = sub_trees[0].create_sub_trees()
        self.assertEqual(4, len(sub_trees))
        size = vec2(1.25, 1.25)
        self.assert_quad_tree(sub_trees[0], vec2(-3.75, 3.75), size)
        self.assert_quad_tree(sub_trees[1], vec2(-1.25, 3.75), size)
        self.assert_quad_tree(sub_trees[2], vec2(-3.75, 1.25), size)
        self.assert_quad_tree(sub_trees[3], vec2(-1.25, 1.25), size)

    def assert_quad_tree(self, tree: QuadTree, position, size_half, max_entities: int = 2):
        self.assertEqual(position, tree.position)
        self.assertEqual(size_half, tree.size_half)
        self.assertEqual(max_entities, tree.max_entities)

    def test_overlaps_tree(self):
        quad_tree = QuadTree(vec2(), vec2(10, 10))
        result = quad_tree.overlaps_tree(vec3(), vec2(5, 5))
        self.assertTrue(result)

        result = quad_tree.overlaps_tree(vec3(7), vec2(5, 5))
        self.assertTrue(result)

        result = quad_tree.overlaps_tree(vec3(7.5), vec2(5, 5))
        self.assertTrue(result)

        result = quad_tree.overlaps_tree(vec3(8), vec2(5, 5))
        self.assertFalse(result)
