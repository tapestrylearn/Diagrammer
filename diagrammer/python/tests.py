import unittest
import model

class LabTests(unittest.TestCase):
    def setUp(self):
        # resetting to initial state
        model.PyObject.clear_directory()

    def test_value_text(self):
        # primitives
        anint = 1
        afloat = 2.5
        abool = True
        astr = 'hello world'
        anone = None

        model = make_model_dict(locals())

        self.assertEqual(model['anint'].export()['text'], '1')
        self.assertEqual(model['afloat'].export()['text'], '2.5')
        self.assertEqual(model['abool'].export()['text'], 'True')
        self.assertEqual(model['astr'].export()['text'], "'hello world'")
        self.assertEqual(model['anone'].export()['text'], 'None')

        # ranges
        range1 = range(5)
        range2 = range(1, 5)
        range3 = range(1, 5, 2)
        range3_default = range(1, 5, 1)

        model = make_model_dict(locals())

        self.assertEqual(model['range1'].export()['text'], '0:5')
        self.assertEqual(model['range2'].export()['text'], '1:5')
        self.assertEqual(model['range3'].export()['text'], '1:5:2')
        self.assertEqual(model['range3_default'].export()['text'], '1:5')

    def test_variable_structure(self):
        anint = 1
        int_model = make_for_obj(anint)
        var_model = model.Variable('test', int_model)

        self.assertEqual(var_model.export()['name'], 'test')
        self.assertEqual(var_model.export()['pyobj'], int_model.export())

    def test_uniqueness(self):
        # two models for the same variable
        anint = 5
        model0 = make_for_obj(anint)
        model1 = make_for_obj(anint)
        self.assertTrue(model0 is model1)

        # different variables
        anint = 5
        intcopy = anint
        intsame = 5
        intdiff = 8

        alist = [1, 2, 3]
        listcopy = alist
        listsame = [1, 2, 3]
        listdiff = [4, 5, 6]

        self.assertTrue(model['anint'] is model['intcopy'])
        self.assertTrue(model['anint'] is model['intsame'])
        self.assertTrue(model['anint'] is not model['intdiff'])

        self.assertTrue(model['alist'] is model['listcopy'])
        self.assertTrue(model['alist'] is not model['listsame'])
        self.assertTrue(model['alist'] is not model['listdiff'])

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
def make_for_obj(obj: object) -> model.PyObject:
    return model.PyObject.make_for_obj(obj)

def make_model_dict(this_locals: {str : object}) -> {str : model.PyObject}:
    return {name : make_for_obj(obj) for name, obj in this_locals.items() if name != 'self'}

if __name__ == '__main__':
    unittest.main()
