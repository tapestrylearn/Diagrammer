import utils
utils.setup_tests()

import unittest
from diagrammer.scene import basic

# NOTE: I used actual values instead of expressions (sometimes) in asserts so that there's no possibility for error in the expressions
# examples: 'name:type'

class DiagrammerSceneTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self._hcol_set = basic.CollectionSettings(5, 10, 2, basic.CollectionSettings.HORIZONTAL)
        self._vcol_set = basic.CollectionSettings(5, 10, 2, basic.CollectionSettings.VERTICAL)

    def setUp(self):
        pass

    def test_basic_shape(self):
        # test constructor
        shape = basic.BasicShape(1.5, 2.5, 'a', 'b')

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

    def test_variable(self):
        var = basic.Variable('name', 'type', (lambda name, type: f'{name}:{type}'), 'value')
        self.assertEqual(var.get_width(), basic.Variable.SIZE)
        self.assertEqual(var.get_height(), basic.Variable.SIZE)
        self.assertEqual(var.get_header(), 'name:type')
        self.assertEqual(var.get_content(), 'value')

    def test_pointer(self):
        head_obj = basic.SceneObject()
        pointer = basic.Pointer('name', 'type', (lambda name, type: f'{name}:{type}'), head_obj)
        self.assertEqual(pointer.get_width(), basic.Variable.SIZE)
        self.assertEqual(pointer.get_height(), basic.Variable.SIZE)
        self.assertEqual(pointer.get_header(), 'name:type')
        self.assertEqual(pointer.get_content(), '')
        self.assertTrue(pointer.get_head_obj() is head_obj)

    def test_basic_value(self):
        basic_val = basic.BasicValue('type', 'value')
        self.assertEqual(basic_val.get_width(), basic.BasicValue.RADIUS * 2)
        self.assertEqual(basic_val.get_height(), basic.BasicValue.RADIUS * 2)
        self.assertEqual(basic_val.get_header(), 'type')
        self.assertEqual(basic_val.get_content(), 'value')

    def test_collection(self):
        # standard horizontal
        col = basic.Collection(self._hcol_set, 'type', 5)
        self.assertEqual(col.get_width(), 5 + basic.Variable.SIZE + 4 * (2 + basic.Variable.SIZE) + 5)
        self.assertEqual(col.get_height(), 10 + basic.Variable.SIZE + 10)
        self.assertEqual(col.get_header(), 'type')
        self.assertEqual(col.get_content(), '')

        # standard vertical
        col = basic.Collection(self._vcol_set, 'type', 5)
        self.assertEqual(col.get_width(), 5 + basic.Variable.SIZE + 5)
        self.assertEqual(col.get_height(), 10 + basic.Variable.SIZE + 4 * (2 + basic.Variable.SIZE) + 10)

        # empty horizontal
        col = basic.Collection(self._hcol_set, 'type', 0)
        self.assertEqual(col.get_width(), 5 + 5)
        self.assertEqual(col.get_height(), 10 + 10)

        # empty vertical
        col = basic.Collection(self._vcol_set, 'type', 0)
        self.assertEqual(col.get_width(), 5 + 5)
        self.assertEqual(col.get_height(), 10 + 10)

    def test_simple_collection(self):
        # width, height, header, content already tested in test_collection

        # horizontal set pos
        vars = [basic.Variable('name', 'type', (lambda name, type: f'{name}:{type}'), value) for value in ['a', 'b', 'c']]
        col = basic.SimpleCollection(self._hcol_set, 'type', vars, True)
        col.set_pos(1.5, 2.5)
        self.assertEqual(col.get_pos(), (1.5, 2.5))
        positions = [(1.5 + 5, 2.5 + 10), (1.5 + 5 + basic.Variable.SIZE + 2, 2.5 + 10), (1.5 + 5 + 2 * (basic.Variable.SIZE + 2), 2.5 + 10)]

        for (i, var) in enumerate(col):
            self.assertEqual(var.get_pos(), positions[i])

        # vertical set pos
        vars = [basic.Variable('name', 'type', (lambda name, type: f'{name}:{type}'), value) for value in ['a', 'b', 'c']]
        col = basic.SimpleCollection(self._vcol_set, 'type', vars, True)
        col.set_pos(3.5, 4.5)
        self.assertEqual(col.get_pos(), (3.5, 4.5))
        positions = [(3.5 + 5, 4.5 + 10), (3.5 + 5, 4.5 + 10 + basic.Variable.SIZE + 2), (3.5 + 5, 4.5 + 10 + 2 * (basic.Variable.SIZE + 2))]

        for (i, var) in enumerate(col):
            self.assertEqual(var.get_pos(), positions[i])

        # reorder (when allowed)
        vars = [basic.Variable('name', 'type', (lambda name, type: f'{name}:{type}'), value) for value in ['a', 'b', 'c']]
        var_a, var_b, var_c = vars
        col = basic.SimpleCollection(self._vcol_set, 'type', vars, True)
        desired_order = [var_a, var_b, var_c]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        col.reorder(0, 0)
        desired_order = [var_a, var_b, var_c]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        col.reorder(0, 1)
        desired_order = [var_b, var_a, var_c]

        for (i, var) in enumerate(col):
            self.assertTrue(var is desired_order[i])

        # reorder (when not allowed)
        col = basic.SimpleCollection(self._vcol_set, 'type', [], False)
        self.assertRaises(basic.ReorderException, col.reorder, 0, 0)

    def test_complex_collection(self):
        # width, height, header, content already tested in test_collection
        # set pos already tested in test_simple_collection

        # vars to use
        var_a, var_b, var_c = (basic.Variable('name', 'type', (lambda name, type: f'{name}:{type}'), value) for value in ['a', 'b', 'c'])
        ref_a, ref_b, ref_c = (basic.Reference('name', 'type', (lambda name, type: f'{name}:{type}'), var) for var in [var_a, var_b, var_c])
        ref_a2 = basic.Reference('name', 'type', (lambda name, type: f'{name}:{type}'), var_a)

        # iter standard
        sections = {'a': [[var_a, ref_a2, ref_a]], 'bc': [[var_b, ref_b], [var_c, ref_c]]}
        section_order = ['bc', 'a']
        col = basic.ComplexCollection(self._hcol_set, 'type', sections, section_order, True)
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
        self.assertEqual(con.get_width(), basic.Container.H_MARGIN + 5 + basic.Variable.SIZE + 4 * (2 + basic.Variable.SIZE) + 5 + basic.Container.H_MARGIN)
        self.assertEqual(con.get_height(), basic.Container.V_MARGIN + 10 + basic.Variable.SIZE + 10 + basic.Container.V_MARGIN)
        self.assertEqual(con.get_header(), 'con_type')
        self.assertEqual(con.get_content(), '')
        self.assertTrue(con.get_col() is col)

    def test_inheritances(self):
        # write an automated system that takes in an InheritanceTree object and uses it to test all classes against each other
        pass


if __name__ == '__main__':
    unittest.main()
