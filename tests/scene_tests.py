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
        self._cell_size = 50
        self._hcol_set = basic.CollectionSettings(5, 10, 2, basic.CollectionSettings.HORIZONTAL, self._cell_size)
        self._vcol_set = basic.CollectionSettings(5, 10, 2, basic.CollectionSettings.VERTICAL, self._cell_size)

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

    def test_collection_contents(self):
        pass

    def test_collection_constructors(self):
        # standard horizontal
        col = basic.Collection()
        col.construct('type', TestCollectionContents(5), self._hcol_set)
        self.assertEqual(col.get_width(), 5 + self._cell_size + 4 * (2 + self._cell_size) + 5)
        self.assertEqual(col.get_height(), 10 + self._cell_size + 10)
        self.assertEqual(col.get_header(), 'type')
        self.assertEqual(col.get_content(), '')
        self.assertEqual(col.get_shape(), basic.Shape.ROUNDED_RECT)

        # standard vertical
        col = basic.Collection()
        col.construct('type', TestCollectionContents(5), self._vcol_set)
        self.assertEqual(col.get_width(), 5 + self._cell_size + 5)
        self.assertEqual(col.get_height(), 10 + self._cell_size + 4 * (2 + self._cell_size) + 10)

        # empty horizontal
        col = basic.Collection()
        col.construct('type', TestCollectionContents(0), self._hcol_set)
        self.assertEqual(col.get_width(), 5 + 5)
        self.assertEqual(col.get_height(), 10 + 10)

        # empty vertical
        col = basic.Collection()
        col.construct('type', TestCollectionContents(0), self._vcol_set)
        self.assertEqual(col.get_width(), 5 + 5)
        self.assertEqual(col.get_height(), 10 + 10)

    '''def test_complex_collection(self):
        # width, height, header, content already tested in test_collection
        # set pos already tested in test_simple_collection

        # vars to use
        var_a, var_b, var_c = (basic.Variable('name:type', value) for value in ['a', 'b', 'c'])
        ref_a, ref_b, ref_c = (basic.Reference('name:type', var) for var in [var_a, var_b, var_c])
        ref_a2 = basic.Reference('name:type', var_a)

        # iter standard
        sections = {'a': [[var_a, ref_a2, ref_a]], 'bc': [[var_b, ref_b], [var_c, ref_c]]}
        section_order = ['bc', 'a']
        col = basic.ComplexCollection(self._hcol_set, 'type', sections, section_order, True)
        self.assertEqual(col.get_shape(), basic.ROUNDED_RECT)
        desired_order = [var_b, ref_b, var_c, ref_c, var_a, ref_a2, ref_a]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        # reorder (iter standard cont.)
        col.reorder('bc', 0, 0)

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        col.reorder('bc', 0, 1)
        desired_order = [var_c, ref_c, var_b, ref_b, var_a, ref_a2, ref_a]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        # reorder_ml (iter standard cont.)
        col.reorder_ml(0, 0, 0)

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        col.reorder_ml(0, 0, 1)
        desired_order = [var_b, ref_b, var_c, ref_c, var_a, ref_a2, ref_a]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        # reorder section (iter standard cont.)
        col.reorder_section(0, 0)

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        col.reorder_section(0, 1)
        desired_order = [var_a, ref_a2, ref_a, var_b, ref_b, var_c, ref_c]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        # iter blank
        sections = {}
        section_order = []
        col = basic.ComplexCollection(self._hcol_set, 'type', sections, section_order, True)

        for (i, var) in enumerate(col):
            pass

        # iter one section
        sections = {'abc': [[var_a, ref_a2, ref_a], [var_b, ref_b], [var_c, ref_c]]}
        section_order = ['abc']
        col = basic.ComplexCollection(self._hcol_set, 'type', sections, section_order, True)
        desired_order = [var_a, ref_a2, ref_a, var_b, ref_b, var_c, ref_c]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        # iter one group per section
        sections = {'a': [[var_a, ref_a2, ref_a]], 'b': [[var_b, ref_b]]}
        section_order = ['a', 'b']
        col = basic.ComplexCollection(self._hcol_set, 'type', sections, section_order, True)
        desired_order = [var_a, ref_a2, ref_a, var_b, ref_b]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        # iter one var per group
        sections = {'ab': [[var_b], [var_a]], 'c': [[var_c]]}
        section_order = ['c', 'ab']
        col = basic.ComplexCollection(self._hcol_set, 'type', sections, section_order, True)
        desired_order = [var_c, var_b, var_a]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        # reorder section (when not allowed)
        col = basic.ComplexCollection(self._hcol_set, 'type', {'a': [[var_a]]}, ['a'], False)
        col.reorder('a', 0, 0) # assert not raises basically
        self.assertRaises(basic.ReorderException, col.reorder_section, 0, 0)

    def test_container(self):
        col = basic.Collection(self._hcol_set, 'col_type', 5)
        con = basic.Container('con_type', col)
        self.assertEqual(con.get_width(), basic.Container.H_MARGIN + 5 + self._cell_size + 4 * (2 + self._cell_size) + 5 + basic.Container.H_MARGIN)
        self.assertEqual(con.get_height(), basic.Container.V_MARGIN + 10 + self._cell_size + 10 + basic.Container.V_MARGIN)
        self.assertEqual(con.get_header(), 'con_type')
        self.assertEqual(con.get_content(), '')
        self.assertEqual(con.get_shape(), basic.ROUNDED_RECT)
        self.assertTrue(con.get_col() is col)

    def test_snapshot(self):
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
        col = basic.Collection(self._hcol_set, 'a', 0)
        self.assertEqual(col.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # simple collection
        vars = [basic.Variable('name:type', value) for value in ['a', 'b', 'c']]
        scol = basic.SimpleCollection(self._hcol_set, 'type', vars, True)
        self.assertEqual(scol.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # complex collection
        var_a, var_b, var_c = (basic.Variable('name:type', value) for value in ['a', 'b', 'c'])
        ref_a, ref_b, ref_c = (basic.Reference('name:type', var) for var in [var_a, var_b, var_c])
        ref_a2 = basic.Reference('name:type', var_a)
        sections = {'a': [[var_a, ref_a2, ref_a]], 'bc': [[var_b, ref_b], [var_c, ref_c]]}
        section_order = ['bc', 'a']
        ccol = basic.ComplexCollection(self._hcol_set, 'type', sections, section_order, True)
        self.assertEqual(ccol.export().keys(), {
            'width', 'height', 'header', 'content', 'x', 'y', 'shape'
        })

        # container
        vars = [basic.Variable('name:type', value) for value in ['a', 'b', 'c']]
        scol = basic.SimpleCollection(self._hcol_set, 'type', vars, True)
        con = basic.Container('a', scol)
        self.assertEqual(con.export().keys(), {
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
