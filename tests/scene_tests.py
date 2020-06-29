import utils
utils.setup_pythonpath_for_tests()

import unittest
from collections import OrderedDict
from diagrammer.scene import basic
import math


class TestCollectionContents(basic.CollectionContents):
    def __init__(self, length: int):
        self._len = length
        self._contents = [basic.BasicShape() for _ in range(length)]

        for shape in self._contents:
            shape.construct(0, 0, '', '')

    def __len__(self) -> int:
        return self._len

    def __iter__(self) -> int:
        return iter(self._contents)


class Circle(basic.BasicShape):
    SHAPE = basic.Shape.CIRCLE


class Square(basic.BasicShape):
    SHAPE = basic.Shape.SQUARE


class DiagrammerSceneTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        # prime numbers so it's impossible that they accidentally multiply to equal each other
        self.hmargin = 5
        self.vmargin = 11
        self.cell_gap = 2
        self.cell_size = 53
        self.con_hmargin = 3
        self.con_vmargin = 7
        self.corner_radius = 19
        self._hcoll_set = basic.CollectionSettings(self.hmargin, self.vmargin, self.cell_gap, basic.CollectionSettings.HORIZONTAL, self.cell_size, self.corner_radius)
        self._vcoll_set = basic.CollectionSettings(self.hmargin, self.vmargin, self.cell_gap, basic.CollectionSettings.VERTICAL, self.cell_size, self.corner_radius)

    def setUp(self):
        pass

    def test_collision(self):
        width = 100
        height = 40
        this = basic.BasicShape()
        this.construct(width, height, '', '')
        other = basic.BasicShape()
        other.construct(width, height, '', '')

        test_poses = [
            (0, 0, 0, 0),
            (0, 0, width / 2, height / 2),
            (0, 0, width - 1, height - 1),
            (0, 0, width, height),
            (0, 0, width + 1, height + 1),
            (width / 2, height / 2, 0, 0),
            (width - 1, height - 1, 0, 0),
            (width, height, 0, 0),
            (width + 1, height + 1, 0, 0),
            (0, 0, width / 2, height * 2),
            (0, 0, width * 2, height / 2),
        ]

        expected_collisions = [True, True, True, False, False, True, True, False, False, False, False]

        for test_pos, expected_collision in zip(test_poses, expected_collisions):
            this.set_pos(test_pos[0], test_pos[1])
            other.set_pos(test_pos[2], test_pos[3])
            self.assertEqual(this.collides(other), expected_collision)

    def test_circle_edge_pos(self):
        circle = basic.Circle()
        radius = 50
        test_x, test_y = (60, 70)
        circle.construct(radius, '', '')
        circle.set_pos(test_x, test_y)

        test_dangles = [(0, 360), (-720, -360), (720, 1080)]

        for start_angle, end_angle in test_dangles:
            for d in range(start_angle, end_angle, 45):
                rounded_result = tuple(round(coord) for coord in circle.calculate_edge_pos(math.radians(d)))
                rounded_expected = (round(test_x + radius * math.cos(math.radians(d))), round(test_y - radius * math.sin(math.radians(d))))
                self.assertEqual(rounded_result, rounded_expected)

    def test_square_edge_pos(self):
        square = basic.Square()
        size = 100
        test_x, test_y = (10, 20)
        square.construct(size, '', '')
        square.set_corner_pos(test_x, test_y)

        test_angles = [(0, 360), (-720, -360), (720, 1080)]
        expected_poses = [
            (test_x + size, test_y + size / 2),
            (test_x + size, test_y),
            (test_x + size / 2, test_y),
            (test_x, test_y),
            (test_x, test_y + size / 2),
            (test_x, test_y + size),
            (test_x + size / 2, test_y + size),
            (test_x + size, test_y + size)
        ]

        for start_angle, end_angle in test_angles:
            for i, d in enumerate(range(start_angle, end_angle, 45)):
                rounded_result = tuple(round(coord) for coord in square.calculate_edge_pos(math.radians(d)))
                self.assertEqual(rounded_result, expected_poses[i])

    def test_rounded_rect_edge_pos(self):
        rounded_rect = basic.RoundedRect()
        radius = 10
        rounded_rect.construct(60, 40, radius, '', '')
        rounded_rect.set_corner_pos(10, 10)

        test_angles = [0, math.atan2(20, 30), math.pi / 2, math.atan2(20, -30), math.pi, math.atan2(-20, -30), 3 * math.pi / 2, math.atan2(-20, 30)]
        expected_poses = [
            (70, 30), (round(60 + radius * math.cos(test_angles[1])), round(20 - radius * math.sin(test_angles[1]))),
            (40, 10), (round(20 + radius * math.cos(test_angles[3])), round(20 - radius * math.sin(test_angles[3]))),
            (10, 30), (round(20 + radius * math.cos(test_angles[5])), round(40 - radius * math.sin(test_angles[5]))),
            (40, 50), (round(60 + radius * math.cos(test_angles[7])), round(40 - radius * math.sin(test_angles[7])))
            ]

        for i, d in enumerate(test_angles):
            rounded_result = tuple(round(coord) for coord in rounded_rect.calculate_edge_pos(d))
            self.assertEqual(rounded_result, expected_poses[i])

    def test_arrow_angles(self):
        tail_obj = basic.BasicShape()
        head_obj = basic.BasicShape()
        arrow = basic.Arrow(tail_obj, head_obj, basic.ArrowSettings(None, None, None))

        tail_obj.construct(50, 50, '', '')
        head_obj.construct(50, 50, '', '')
        tail_obj.set_pos(100, 100)

        head_poses = [(200, 100), (200, 0), (100, 0), (0, 0), (0, 100), (0, 200), (100, 200), (200, 200)]
        expected_tail_angles = [0, 45, 90, 135, 180, -135, -90, -45]
        expected_head_angles = [180, -135, -90, -45, 0, 45, 90, 135]

        for (i, head_pos) in enumerate(head_poses):
            head_obj.set_pos(*head_poses[i])
            self.assertEqual(expected_tail_angles[i], round(math.degrees(arrow.get_tail_angle())))
            self.assertEqual(expected_head_angles[i], round(math.degrees(arrow.get_head_angle())))

    def test_get_center_end_pos(self):
        tail_obj = basic.BasicShape()
        head_obj = basic.BasicShape()
        arrow = basic.Arrow(tail_obj, head_obj, basic.ArrowSettings(None, basic.ArrowSettings.CENTER, basic.ArrowSettings.CENTER))

        tail_obj.construct(50, 50, '', '')
        head_obj.construct(50, 50, '', '')
        tail_obj.set_pos(0, 0)
        head_obj.set_pos(200, 200)

        self.assertEqual(arrow.get_tail_pos(), (0, 0))
        self.assertEqual(arrow.get_head_pos(), (200, 200))

    def test_get_center_end_pos(self):
        tail_obj = basic.Square()
        head_obj = basic.Square()
        arrow = basic.Arrow(tail_obj, head_obj, basic.ArrowSettings(None, basic.ArrowSettings.EDGE, basic.ArrowSettings.EDGE))

        tail_obj.construct(50, '', '')
        head_obj.construct(50, '', '')
        tail_obj.set_pos(0, 0)
        head_obj.set_pos(100, 100)

        self.assertEqual(tuple(round(coord) for coord in arrow.get_tail_pos()), (25, 25))
        self.assertEqual(tuple(round(coord) for coord in arrow.get_head_pos()), (75, 75))

    def test_end_pos_caching(self):
        tail_obj = basic.Square()
        head_obj = basic.Square()
        arrow = basic.Arrow(tail_obj, head_obj, basic.ArrowSettings(None, basic.ArrowSettings.EDGE, basic.ArrowSettings.EDGE))

        tail_obj.construct(50, '', '')
        head_obj.construct(50, '', '')
        tail_obj.set_pos(0, 0)
        head_obj.set_pos(100, 100)

        # check that the same call twice works the same
        self.assertEqual(tuple(round(coord) for coord in arrow.get_tail_pos()), (25, 25))
        self.assertEqual(tuple(round(coord) for coord in arrow.get_tail_pos()), (25, 25))
        self.assertEqual(tuple(round(coord) for coord in arrow.get_head_pos()), (75, 75))
        self.assertEqual(tuple(round(coord) for coord in arrow.get_head_pos()), (75, 75))

        # check that reposition recaches
        tail_obj.set_pos(200, 0)

        self.assertEqual(tuple(round(coord) for coord in arrow.get_tail_pos()), (175, 25))
        self.assertEqual(tuple(round(coord) for coord in arrow.get_tail_pos()), (175, 25))
        self.assertEqual(tuple(round(coord) for coord in arrow.get_head_pos()), (125, 75))
        self.assertEqual(tuple(round(coord) for coord in arrow.get_head_pos()), (125, 75))

        # check that caching actually happens
        self.assertEqual(arrow._get_end_pos(basic.Arrow.HEAD, say_cached = True), 'cached')

    def test_basic_shape(self):
        # test constructor
        shape = basic.BasicShape()
        shape.construct(1.5, 2.5, 'a', 'b')

        self.assertEqual(shape.get_width(), 1.5)
        self.assertEqual(shape.get_height(), 2.5)
        self.assertEqual(shape.get_header(), 'a')
        self.assertEqual(shape.get_content(), 'b')
        self.assertEqual(shape.get_x(), None)
        self.assertEqual(shape.get_y(), None)
        self.assertEqual(shape.get_pos(), (None, None))

        # test set pos functions
        shape.set_x(3.5)
        shape.set_y(4.5)
        self.assertEqual(shape.get_x(), 3.5)
        self.assertEqual(shape.get_y(), 4.5)
        self.assertEqual(shape.get_pos(), (3.5, 4.5))

        shape.set_pos(5.5, 6.5)
        self.assertEqual(shape.get_x(), 5.5)
        self.assertEqual(shape.get_y(), 6.5)
        self.assertEqual(shape.get_pos(), (5.5, 6.5))

        # TODO: test stuff that should raise errors

    def test_collection_constructs(self):
        # standard horizontal
        coll = basic.Collection()
        coll.construct('type', TestCollectionContents(5), self._hcoll_set)
        self.assertEqual(coll.get_width(), self.hmargin + self.cell_size + 4 * (self.cell_gap + self.cell_size) + self.hmargin)
        self.assertEqual(coll.get_height(), self.vmargin + self.cell_size + self.vmargin)
        self.assertEqual(coll.get_header(), 'type')
        self.assertEqual(coll.get_content(), '')
        self.assertEqual(coll.get_shape(), basic.Shape.ROUNDED_RECT)

        # standard vertical
        coll = basic.Collection()
        coll.construct('type', TestCollectionContents(5), self._vcoll_set)
        self.assertEqual(coll.get_width(), self.hmargin + self.cell_size + self.hmargin)
        self.assertEqual(coll.get_height(), self.vmargin + self.cell_size + 4 * (self.cell_gap + self.cell_size) + self.vmargin)

        # empty horizontal
        coll = basic.Collection()
        coll.construct('type', TestCollectionContents(0), self._hcoll_set)
        self.assertEqual(coll.get_width(), self.hmargin + self.hmargin)
        self.assertEqual(coll.get_height(), self.vmargin + self.vmargin)

        # empty vertical
        coll = basic.Collection()
        coll.construct('type', TestCollectionContents(0), self._vcoll_set)
        self.assertEqual(coll.get_width(), self.hmargin + self.hmargin)
        self.assertEqual(coll.get_height(), self.vmargin + self.vmargin)

    def test_collection_setting_pos(self):
        # horizontal
        coll = basic.Collection()
        coll.construct('type', TestCollectionContents(5), self._hcoll_set)
        test_x, test_y = (10, 20)
        coll.set_corner_pos(test_x, test_y)

        self.assertEqual(coll.get_corner_x(), test_x)
        self.assertEqual(coll.get_corner_y(), test_y)

        for (i, element) in enumerate(coll.get_contents()):
            self.assertEqual(element.get_corner_x(), test_x + self.hmargin + i * (self.cell_size + self.cell_gap))
            self.assertEqual(element.get_corner_y(), test_y + self.vmargin)

        # vertical
        coll = basic.Collection()
        coll.construct('type', TestCollectionContents(5), self._vcoll_set)
        # I use set_corner_x/y instead of pos to make sure both work correctly
        coll.set_corner_x(test_x)
        coll.set_corner_y(test_y)

        self.assertEqual(coll.get_corner_pos(), (test_x, test_y))

        for (i, element) in enumerate(coll.get_contents()):
            self.assertEqual(element.get_corner_x(), test_x + self.hmargin)
            self.assertEqual(element.get_corner_y(), test_y + self.vmargin + i * (self.cell_size + self.cell_gap))

    def test_container(self):
        # standard collection
        coll = basic.Collection()
        coll.construct('coll_type', TestCollectionContents(5), self._hcoll_set)
        container = basic.Container()
        container.construct('con_type', coll, self.con_hmargin, self.con_vmargin, self.corner_radius)
        self.assertEqual(container.get_width(), self.con_hmargin + self.hmargin + self.cell_size + 4 * (self.cell_gap + self.cell_size) + self.hmargin + self.con_hmargin)
        self.assertEqual(container.get_height(), self.con_vmargin + self.vmargin + self.cell_size + self.vmargin + self.con_vmargin)
        self.assertEqual(container.get_header(), 'con_type')
        self.assertEqual(container.get_content(), '')
        self.assertEqual(container.get_shape(), basic.Shape.ROUNDED_RECT)
        self.assertTrue(container.get_coll() is coll)

        # empty collection
        coll = basic.Collection()
        coll.construct('coll_type', TestCollectionContents(0), self._hcoll_set)
        container = basic.Container()
        container.construct('con_type', coll, self.con_hmargin, self.con_vmargin, self.corner_radius)
        self.assertEqual(container.get_width(), self.con_hmargin + self.hmargin + self.hmargin + self.con_hmargin)
        self.assertEqual(container.get_height(), self.con_vmargin + self.vmargin + self.vmargin + self.con_vmargin)
        self.assertEqual(container.get_header(), 'con_type')
        self.assertEqual(container.get_content(), '')
        self.assertEqual(container.get_shape(), basic.Shape.ROUNDED_RECT)
        self.assertTrue(container.get_coll() is coll)

    '''def test_snapshot(self):
        scne0 = basic.Scene([])
        scne1 = basic.Scene([])
        scenes = OrderedDict([('0', scne0), ('1', scne1)])
        snap = basic.Snapshot(scenes)
        self.assertTrue(snap.get_scenes() is scenes)
        self.assertTrue(snap.get_scene('0') is scne0)
        self.assertTrue(snap.get_scene('1') is scne1)

    def test_inheritances(self):
        # write an automated system that takes in an InheritanceTree object and uses it to test all classes against each other
        pass

    def test_export_keys(self):
        # scene object
        obj = basic.SceneObject()
        self.assertEqual(obj.export(), {})

        # basic shape
        shape = basic.BasicShape(1.5, 2.5, 'a', 'b')
        self.assertEqual(shape.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # variable
        var = basic.Variable('a', 'b')
        self.assertEqual(var.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # pointer
        point = basic.Pointer('a', shape)
        self.assertEqual(point.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # reference
        ref = basic.Reference('a', shape)
        self.assertEqual(ref.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # value
        val = basic.Value(1.5, 2.5, 'a', 'b')
        self.assertEqual(val.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # basic value
        bval = basic.BasicValue('a', 'b')
        self.assertEqual(bval.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # collection
        coll = basic.Collection(self._hcoll_set, 'a', 0)
        self.assertEqual(coll.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # simple collection
        vars = [basic.Variable('name:type', value) for value in ['a', 'b', 'c']]
        scoll = basic.SimpleCollection(self._hcoll_set, 'type', vars, True)
        self.assertEqual(scoll.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # complex collection
        var_a, var_b, var_c = (basic.Variable('name:type', value) for value in ['a', 'b', 'c'])
        ref_a, ref_b, ref_c = (basic.Reference('name:type', var) for var in [var_a, var_b, var_c])
        ref_a2 = basic.Reference('name:type', var_a)
        sections = {'a': [[var_a, ref_a2, ref_a]], 'bc': [[var_b, ref_b], [var_c, ref_c]]}
        section_order = ['bc', 'a']
        ccoll = basic.ComplexCollection(self._hcoll_set, 'type', sections, section_order, True)
        self.assertEqual(ccoll.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # container
        vars = [basic.Variable('name:type', value) for value in ['a', 'b', 'c']]
        scoll = basic.SimpleCollection(self._hcoll_set, 'type', vars, True)
        container = basic.Container('a', scoll)
        self.assertEqual(container.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # snapshot
        scne2 = basic.Scene([shape, var])
        snap = basic.Snapshot(OrderedDict([('a', scne), ('b', scne2)]))
        self.assertEqual(snap.export().keys(), {
            'a', 'b'
        })'''


if __name__ == '__main__':
    unittest.main(verbosity=2)
