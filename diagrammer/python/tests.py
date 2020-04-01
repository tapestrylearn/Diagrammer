import unittest

import model
import __init__ as core

# --- MODEL TESTS ---
class DiagrammerModelTests(unittest.TestCase):
    def setUp(self):
        # resetting to initial state
        model.PyObject.clear_directory()

    def test_value_text(self):
        # primitives
        int_model = self.make_for_obj(1)
        self.assertEqual(int_model.export()['text'], '1')

        float_model = self.make_for_obj(2.5)
        self.assertEqual(float_model.export()['text'], '2.5')

        bool_model = self.make_for_obj(True)
        self.assertEqual(bool_model.export()['text'], 'True')

        str_model = self.make_for_obj('hello world')
        self.assertEqual(str_model.export()['text'], "'hello world'")

        none_model = self.make_for_obj(None)
        self.assertEqual(none_model.export()['text'], 'None')

        # ranges
        r = range(5)
        range1_model = self.make_for_obj(r)
        self.assertEqual(range1_model.export()['text'], '0:5')

        r = range(1, 5)
        range2_model = self.make_for_obj(r)
        self.assertEqual(range2_model.export()['text'], '1:5')

        r = range(1, 5, 2)
        range3_model = self.make_for_obj(r)
        self.assertEqual(range3_model.export()['text'], '1:5:2')

        r = range(1, 5, 1)
        range3_default_model = self.make_for_obj(r)
        self.assertEqual(range3_default_model.export()['text'], '1:5')

    def test_variable_structure(self):
        pass

    def test_diagrammer_collection_uniqueness(self):
        pass

    def test_nested_collection_structure(self):
        # simple nested
        x = [1, 2, 3]
        y = [x, 2, 3]
        y_model = self.make_for_obj(y)

    def test_value_position(self):
        pass

    def test_collection_positions(self):
        pass

    def test_namespace_positions(self):
        pass

    def make_for_obj(self, obj: object) -> model.PyObject:
        return model.PyObject.make_for_obj(obj)



# --- CORE TESTS ---
class DiagrammerPythonCoreTests(unittest.TestCase):
    def setUp(self):
        self.code_sample_basic = 'x = 1\ny = 2\nz = 3'
        self.code_sample_medium = 'x = 1\nif x == 1:\n\tb = x\nelse:\n\tb = 2'
        self.code_sample_advanced = 'x = 5\nfor i in range(x):\n\tb = i'

        self.flags_basic = [1]
        self.flags_medium = [2]
        self.flags_advanced = [2]

    def test_run_code(self):
        result_basic = core._run_code(self.code_sample_basic, self.flags_basic)
        print(result_basic[0], end='\n\n')

        # result_medium = core._run_code(self.code_sample_medium, self.flags_medium)
        # print(result_medium, end='\n\n')

        # result_advanced = core._run_code(self.code_sample_advanced, self.flags_advanced)
        # print(result_advanced, end='\n\n')


if __name__ == '__main__':
    unittest.main()
