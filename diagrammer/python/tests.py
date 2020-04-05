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
        self.code_sample_conditional = 'x = 1\nif x == 1:\n\tb = x\nelse:\n\tb = 2'
        self.code_sample_loop = 'x = 5\nfor i in range(x):\n\tb = i'

        self.flags_basic = [1]
        self.flags_medium = [2]
        self.flags_advanced = [2]

    def test_run_code(self):
        result_basic = core._run_code(self.code_sample_basic, self.flags_basic)
        self.assertEqual([self.snapshot_as_vardict(snapshot) for snapshot in result_basic], [
            {
                'globals' : {'x' : '1', 'y' : '2'},
                'locals' : {'x' : '1', 'y' : '2'}
            }
        ])

        result_conditional = core._run_code(self.code_sample_conditional, self.flags_medium)
        self.assertEqual([self.snapshot_as_vardict(snapshot) for snapshot in result_conditional], [
            {
                'globals' : {'x' : '1', 'b' : '1'},
                'locals' : {'x' : '1', 'b' : '1'}
            }
        ])

        result_loop = core._run_code(self.code_sample_loop, self.flags_advanced)
        self.assertEqual([self.snapshot_as_vardict(snapshot) for snapshot in result_loop], [
            {
                'globals' : {'x' : '5', 'b' : '0', 'i' : '0'},
                'locals' : {'x' : '5', 'b' : '0', 'i' : '0'}
            },
            {
                'globals' : {'x' : '5', 'b' : '1', 'i' : '1'},
                'locals' : {'x' : '5', 'b' : '1', 'i' : '1'}
            },
            {
                'globals' : {'x' : '5', 'b' : '2', 'i' : '2'},
                'locals' : {'x' : '5', 'b' : '2', 'i' : '2'}
            },
            {
                'globals' : {'x' : '5', 'b' : '3', 'i' : '3'},
                'locals' : {'x' : '5', 'b' : '3', 'i' : '3'}
            },
            {
                'globals' : {'x' : '5', 'b' : '4', 'i' : '4'},
                'locals' : {'x' : '5', 'b' : '4', 'i' : '4'}
            }
        ])


    def snapshot_as_vardict(self, snapshot: model.Snapshot) -> {str : str}:
        return {
            'globals' : {var.get_name() : var.get_value().get_text() for var in snapshot._globals._variables},
            'locals' : {var.get_name() : var.get_value().get_text() for var in snapshot._locals._variables},
        }


if __name__ == '__main__':
    unittest.main()
