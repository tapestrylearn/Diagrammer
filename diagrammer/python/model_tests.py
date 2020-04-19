import unittest

import model

class DiagrammerModelTests(unittest.TestCase):
    def setUp(self):
        # resetting to initial state
        model.PyObject.clear_directory()

    def test_basic_variable_and_value(self):
        anint = 1

        objs, vars = self.make_models(locals())

        # variable
        self.assertEqual({key: val for key, val in vars['anint'].export().items() if key != 'pyobj'}, {
            'name': 'anint'
        })

        # value
        self.assertEqual(objs['anint'].export(), {
            'type': 'int',
            'text': '1'
        })

    def test_basic_collection(self):
        alist = [1, 2, 3]

        objs, _ = self.make_models(locals())

        # outer layer
        self.assertEqual({key: val for key, val in objs['alist'].export().items() if key != 'vars'}, {
            'type': 'list'
        })

        # variables
        for i, json in enumerate([{key: val for key, val in var.items() if key != 'pyobj'} for var in objs['alist'].export()['vars']]):
            self.assertEqual(json, {
                'name': f'{i}',
            })

        # ints the variables point to
        for i, json in enumerate([var['pyobj'] for var in objs['alist'].export()['vars']]):
            self.assertEqual(json, {
                'type': 'int',
                'text': f'{i + 1}'
            })

    def test_basic_instance(self):
        class H:
            hi = 5

            def high5():
                pass

        objs, _ = self.make_models(locals())

        namespace = objs['H'].get_namespace()

        # instance
        self.assertEqual({key: val for key, val in objs['H'].export().items() if key != 'namespace'}, {
            'type': 'type'
        })

        # namespace
        self.assertEqual({key: val for key, val in namespace.export().items() if key != 'vars'}, {
            'type': 'mappingproxy'
        })

        # variables
        self.assertEqual({var['name'] for var in namespace.export()['vars']}, {
            'hi', 'high5'
        })

        # values the variables point to
        for var in namespace.export()['vars']:
            if var['name'] == 'hi':
                self.assertEqual(var['pyobj'], {
                    'type': 'int',
                    'text': '5'
                })
            elif var['name'] == 'high5':
                self.assertEqual(var['pyobj'], {
                    'type': 'function',
                    'namespace': {
                        'type': 'dict',
                        'vars': []
                    }
                })

    def test_primitive_value_text(self):
        # primitives
        anint = 1
        afloat = 2.5
        abool = True
        astr = 'hello world'
        anone = None

        objs, _ = self.make_models(locals())

        self.assertEqual(objs['anint'].export()['text'], '1')
        self.assertEqual(objs['afloat'].export()['text'], '2.5')
        self.assertEqual(objs['abool'].export()['text'], 'True')
        self.assertEqual(objs['astr'].export()['text'], "'hello world'")
        self.assertEqual(objs['anone'].export()['text'], 'None')

        # ranges
        range1 = range(5)
        range2 = range(1, 5)
        range3 = range(1, 5, 2)
        range3_default = range(1, 5, 1)

        objs, _ = self.make_models(locals())

        self.assertEqual(objs['range1'].export()['text'], '0:5')
        self.assertEqual(objs['range2'].export()['text'], '1:5')
        self.assertEqual(objs['range3'].export()['text'], '1:5:2')
        self.assertEqual(objs['range3_default'].export()['text'], '1:5')

    def test_empty_collection(self):
        '''note: an empty namespace is already tested in test_basic_instance'''
        alist = []

        objs, _ = self.make_models(locals())

        self.assertEqual(objs['alist'].export(), {
            'type': 'list',
            'vars': []
        })

    def test_uniqueness(self):
        # two models for the same variable
        anint = 5
        model0 = model.PyObject.make_for_obj(anint)
        model1 = model.PyObject.make_for_obj(anint)
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

        objs, _ = self.make_models(locals())

        self.assertTrue(objs['anint'] is objs['intcopy'])
        self.assertTrue(objs['anint'] is objs['intsame'])
        self.assertTrue(objs['anint'] is not objs['intdiff'])

        self.assertTrue(objs['alist'] is objs['listcopy'])
        self.assertTrue(objs['alist'] is not objs['listsame'])
        self.assertTrue(objs['alist'] is not objs['listdiff'])

        # simple nested list
        x = [3, 8, 6]
        y = [x, 4, 0]

        objs, vars = self.make_models(locals())

        self.assertTrue(objs['x'] is objs['y'].get_variables()[0].get_pyobj())
        self.assertTrue(vars['x'] is not objs['y'].get_variables()[0])

        # self-referential list
        z = [7, 8, 5]
        z[0] = z

        x = [3, 8, 6]
        y = [x, 4, 0]
        x[2] = y

        objs, vars = self.make_models(locals())

        self.assertTrue(objs['z'] is objs['z'].get_variables()[0].get_pyobj())

        self.assertTrue(objs['x'] is objs['y'].get_variables()[0].get_pyobj())
        self.assertTrue(objs['y'] is objs['x'].get_variables()[2].get_pyobj())
        self.assertTrue(vars['x'] is not objs['y'].get_variables()[0])
        self.assertTrue(vars['y'] is not objs['x'].get_variables()[2])

        # self-referential class and __dict__
        class A():
            pass

        a = A()
        a.my_copy = a
        a.my_namespace = a.__dict__

        pyobj, _ = self.make_models_for_obj('a', a)

        for var in pyobj.get_namespace().get_variables():
            if var.get_name() == 'my_copy':
                self.assertTrue(pyobj is var.get_pyobj())
            elif var.get_name() == 'my_namespace':
                self.assertTrue(pyobj.get_namespace() is var.get_pyobj())

        # TODO: self indirect referential objects

    def test_namespace_blacklist(self):
        pass

    def make_for_obj(self, obj: object) -> model.PyObject:
        return model.PyObject.make_for_obj(obj)

    def make_models_for_obj(self, name: str, obj: object) -> (model.PyObject, model.Variable):
        pyobj = model.PyObject.make_for_obj(obj)
        var = model.Variable(name, pyobj)

        return (pyobj, var)

    def make_models(self, this_locals: {str : object}) -> (dict, dict):
        # first bug (uncomment this line and comment out the "second bug" line)
        # objs = {name : model.PyObject.make_for_obj(obj) for name, obj in this_locals.items() if name != 'self'}
        # second bug (uncomment this line and comment out the "first bug" line)
        objs = {name : model.PyObject.make_for_obj(obj) for name, obj in this_locals.items() if name != 'self' and name != 'objs' and name != 'vars'}

        vars = {name : model.Variable(name, obj) for name, obj in objs.items()}
        return (objs, vars)

if __name__ == '__main__':
    unittest.main()
