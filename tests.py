import unittest
from diagrammer import model

class LabTests(unittest.TestCase):
    def setUp(self):
        # resetting to initial state
        model.PyObject.clear_directory()

    def test_value_text(self):
        # primitives
        int_model = make_for_obj(1)
        self.assertEqual(int_model.export()['text'], '1')

        float_model = make_for_obj(2.5)
        self.assertEqual(float_model.export()['text'], '2.5')

        bool_model = make_for_obj(True)
        self.assertEqual(bool_model.export()['text'], 'True')

        str_model = make_for_obj('hello world')
        self.assertEqual(str_model.export()['text'], "'hello world'")

        none_model = make_for_obj(None)
        self.assertEqual(none_model.export()['text'], 'None')

        # ranges
        range1_model = make_for_obj(range(5))
        self.assertEqual(range1_model.export()['text'], '0:5')

        range2_model = make_for_obj(range(1, 5))
        self.assertEqual(range2_model.export()['text'], '1:5')

        range3_model = make_for_obj(range(1, 5, 2))
        self.assertEqual(range3_model.export()['text'], '1:5:2')

        range3_default_model = make_for_obj(range(1, 5, 1))
        self.assertEqual(range3_default_model.export()['text'], '1:5')

    def test_variable_structure(self):
        pass

    def test_diagrammer_collection_uniqueness(self):
        pass

    def test_nested_collection_structure(self):
        # simple nested
        x = [1, 2, 3]
        y = [x, 2, 3]
        y_model = make_for_obj(y)

    def test_value_position(self):
        pass

    def test_collection_positions(self):
        pass

    def test_namespace_positions(self):
        pass


# helper functions
def make_for_obj(obj: object):
    model.PyObject.make_for_obj(obj)

if __name__ == '__main__':
    unittest.main()
