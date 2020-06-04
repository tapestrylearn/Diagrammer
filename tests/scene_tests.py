import utils
utils.setup_pythonpath_for_tests()

import unittest
from collections import OrderedDict
from diagrammer.scene import basic

# NOTE: I used actual values instead of expressions (sometimes) in asserts so that there's no possibility for error in the expressions
# examples: 'name:type'
class TestCollectionContents(basic.CollectionContents):
    def __init__(self, length: int):
        self._len = length

    def __len__(self) -> int:
        return self._len


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
        self._hcoll_set = basic.CollectionSettings(self.hmargin, self.vmargin, self.cell_gap, basic.CollectionSettings.HORIZONTAL, self.cell_size)
        self._vcoll_set = basic.CollectionSettings(self.hmargin, self.vmargin, self.cell_gap, basic.CollectionSettings.VERTICAL, self.cell_size)

    def setUp(self):
        pass

    def test_basic_shape(self):
        # test constructor
        shape = basic.BasicShape()
        shape.construct(1.5, 2.5, 'a', 'b')

        self.assertEqual(shape.get_width(), 1.5)
        self.assertEqual(shape.get_height(), 2.5)
        self.assertEqual(shape.get_header(), 'a')
        self.assertEqual(shape.get_content(), 'b')
        self.assertEqual(shape.get_x(), 0)
        self.assertEqual(shape.get_y(), 0)
        self.assertEqual(shape.get_pos(), (0, 0))

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

    def test_colllection_contents(self):
        pass

    def test_colllection_constructors(self):
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

    def test_container(self):
        # standard colllection
        coll = basic.Collection()
        coll.construct('coll_type', TestCollectionContents(5), self._hcoll_set)
        container = basic.Container()
        container.construct('con_type', coll, self.con_hmargin, self.con_vmargin)
        self.assertEqual(container.get_width(), self.con_hmargin + self.hmargin + self.cell_size + 4 * (self.cell_gap + self.cell_size) + self.hmargin + self.con_hmargin)
        self.assertEqual(container.get_height(), self.con_vmargin + self.vmargin + self.cell_size + self.vmargin + self.con_vmargin)
        self.assertEqual(container.get_header(), 'con_type')
        self.assertEqual(container.get_content(), '')
        self.assertEqual(container.get_shape(), basic.Shape.ROUNDED_RECT)
        self.assertTrue(container.get_coll() is coll)

        # empty colllection
        coll = basic.Collection()
        coll.construct('coll_type', TestCollectionContents(0), self._hcoll_set)
        container = basic.Container()
        container.construct('con_type', coll, self.con_hmargin, self.con_vmargin)
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

        # colllection
        coll = basic.Collection(self._hcoll_set, 'a', 0)
        self.assertEqual(coll.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # simple colllection
        vars = [basic.Variable('name:type', value) for value in ['a', 'b', 'c']]
        scoll = basic.SimpleCollection(self._hcoll_set, 'type', vars, True)
        self.assertEqual(scoll.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # complex colllection
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
    unittest.main()
