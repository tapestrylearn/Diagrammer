
import unittest
from diagrammer import model

class LabTests(unittest.TestCase):
    def setUp(self):
        # resetting to initial state
        model.PyObject.clear_directory()

        # primitives
        self.int_model = model.PyObject.make_for_obj(1)
        self.float_model = model.PyObject.make_for_obj(2.5)
        self.bool_model = model.PyObject.make_for_obj(True)
        self.str_model = model.PyObject.make_for_obj('hello, world')
        self.none_model = model.PyObject.make_for_obj(None)

        # builtin objects
        r1 = range(5)
        r2 = range(1, 5)
        r3 = range(1, 5, 2)
        r3_default = range(1, 5, 1)
        self.range1_obj_model = model.PyObject.make_for_obj(r1)
        self.range2_obj_model = model.PyObject.make_for_obj(r2)
        self.range3_obj_model = model.PyObject.make_for_obj(r3)
        self.range3_default_obj_model = model.PyObject.make_for_obj(r3_default)

        # custom objects
        class A:
            def __init__(self, n: int):
                self.n = n

        self.custom_obj_model = model.PyObject.make_for_obj(A(5))

        # collections
        self.list_model = model.PyObject.make_for_obj([1, 2, 3])
        self.tuple_model = model.PyObject.make_for_obj(('a', 'b', 'c'))
        self.set_model = model.PyObject.make_for_obj({1, 2, 3})
        self.dict_model = model.PyObject.make_for_obj({'a' : 1, 'b' : 2, 'c' : 3})

        # variables
        self.primitive_var = model.Variable('x', self.int_model)
        self.range_obj_var = model.Variable('r', self.range1_obj_model)
        self.custom_obj_var = model.Variable('a', self.custom_obj_model)


    def test_diagrammer_model_creation(self):
        # Value
        self.assertEqual(self.int_model.get_text(), '1')
        self.assertEqual(self.float_model.get_text(), '2.5')
        self.assertEqual(self.bool_model.get_text(), 'True')
        self.assertEqual(self.str_model.get_text(), "'hello, world'")
        self.assertEqual(self.none_model.get_text(), 'None')
        self.assertEqual(self.range1_obj_model.get_text(), '0:5')
        self.assertEqual(self.range2_obj_model.get_text(), '1:5')
        self.assertEqual(self.range3_obj_model.get_text(), '1:5:2')
        self.assertEqual(self.range3_default_obj_model.get_text(), '1:5')

        # Variable
        self.assertEqual(self.primitive_var.get_name(), 'x')
        self.assertTrue(self.primitive_var.get_value() is self.int_model)
        self.assertEqual(self.primitive_var.get_value().get_text(), self.int_model.get_text())

        self.assertEqual(self.range_obj_var.get_name(), 'r')
        self.assertTrue(self.range_obj_var.get_value() is self.range1_obj_model)
        self.assertEqual(self.range_obj_var.get_value().get_text(), self.range1_obj_model.get_text())

        self.assertEqual(self.custom_obj_var.get_name(), 'a')
        self.assertTrue(self.custom_obj_var.get_value() is self.custom_obj_model)
        self.assertEqual(self.custom_obj_var.get_value().export(), self.custom_obj_model.export())


    def test_diagrammer_individual_model_export(self):
        # Value
        self.assertEqual(self.int_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 50,
            'height' : 50,
            'type' : 'int',
            'text' : '1',
        })

        self.assertEqual(self.float_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 50,
            'height' : 50,
            'type' : 'float',
            'text' : '2.5',
        })

        self.assertEqual(self.bool_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 50,
            'height' : 50,
            'type' : 'bool',
            'text' : 'True',
        })

        self.assertEqual(self.str_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 50,
            'height' : 50,
            'type' : 'str',
            'text' : "'hello, world'",
        })

        self.assertEqual(self.range1_obj_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 50,
            'height' : 50,
            'type' : 'range',
            'text' : '0:5',
        })

        self.assertEqual(self.custom_obj_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 70,
            'height' : 70,
            'type' : '__main__.LabTests.setUp.<locals>.A',
            'vars' : [
                {
                    'height': 50,
                    'name': 'n',
                    'value': {
                        'height': 50,
                        'text': '5',
                        'type': 'int',
                        'width': 50,
                        'x': 0,
                        'y': 0
                    },
                    'width': 50,
                    'x': 0,
                    'y': 0,
                }
            ],
        })


        # Collection
        self.assertEqual(self.list_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 170,
            'height' : 70,
            'type' : 'list',
            'vars' : [
                model.Variable('0', model.PyObject.make_for_obj(1)).export(),
                model.Variable('1', model.PyObject.make_for_obj(2)).export(),
                model.Variable('2', model.PyObject.make_for_obj(3)).export(),
            ],
        })

        self.assertEqual(self.tuple_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 170,
            'height' : 70,
            'type' : 'tuple',
            'vars' : [
                model.Variable('0', model.PyObject.make_for_obj('a')).export(),
                model.Variable('1', model.PyObject.make_for_obj('b')).export(),
                model.Variable('2', model.PyObject.make_for_obj('c')).export(),
            ],
        })

        self.assertEqual(self.set_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 170,
            'height' : 70,
            'type' : 'set',
            'vars' : [
                model.Variable('', model.PyObject.make_for_obj(1)).export(),
                model.Variable('', model.PyObject.make_for_obj(2)).export(),
                model.Variable('', model.PyObject.make_for_obj(3)).export(),
            ],
        })

        self.assertEqual(self.dict_model.export(), {
            'x' : 0,
            'y' : 0,
            'width' : 170,
            'height' : 70,
            'type' : 'dict',
            'vars' : [
                model.Variable('a', model.PyObject.make_for_obj(1)).export(),
                model.Variable('b', model.PyObject.make_for_obj(2)).export(),
                model.Variable('c', model.PyObject.make_for_obj(3)).export(),
            ],
        })


    def test_diagrammer_collection_uniqueness(self):
        # int same number
        int1 = 1
        int2 = 1
        self.assertTrue(model.PyObject.make_for_obj(int1) is model.PyObject.make_for_obj(int2))

        # int different number
        int2 = 2

        self.assertTrue(model.PyObject.make_for_obj(int1) is not model.PyObject.make_for_obj(int2))

        # ints inside a list
        collection = model.PyObject.make_for_obj([1, 2, 1])
        self.assertEqual(len({id(var.get_value()) for var in collection.get_variables()}), 2)

        # same list
        x = [1, 2, 3]
        y = x
        x_obj = model.PyObject.make_for_obj(x)
        y_obj = model.PyObject.make_for_obj(y)
        self.assertTrue(x_obj is y_obj)

        # same contents different list
        x = [1, 2, 3]
        y = [1, 2, 3]
        x_obj = model.PyObject.make_for_obj(x)
        y_obj = model.PyObject.make_for_obj(y)
        self.assertTrue(x_obj is not y_obj)


if __name__ == '__main__':
    unittest.main()
