import unittest

import model
import __init__ as diagrammer

# --- MODEL TESTS ---
class DiagrammerModelTests(unittest.TestCase):
    def setUp(self):
        # resetting to initial state
        model.PyObject.clear_directory()

    def test_basic_variable_and_value(self):
        anint = 1

        objs, vars = self.make_models(locals())
        vars['anint'].set_pos(20, 25)
        objs['anint'].set_pos(30, 35)

        # variable
        self.assertEqual({key: val for key, val in vars['anint'].export().items() if key != 'pyobj'}, {
            'x': 20,
            'y': 25,
            'width': model.Variable.SIZE,
            'height': model.Variable.SIZE,
            'name': 'anint'
        })

        # value
        self.assertEqual(objs['anint'].export(), {
            'x': 30,
            'y': 35,
            'width': model.Value.RADIUS * 2,
            'height': model.Value.RADIUS * 2,
            'type': 'int',
            'text': '1'
        })

    def test_basic_stdcollection(self):
        alist = [1, 2, 3]

        objs, _ = self.make_models(locals())

        x, y = (30, 35)
        objs['alist'].set_pos(x, y)

        # outer layer
        self.assertEqual({key: val for key, val in objs['alist'].export().items() if key != 'vars'}, {
            'x': x,
            'y': y,
            'width': model.StdCollection.H_MARGIN * 2 + model.Variable.SIZE * len(alist),
            'height': model.StdCollection.V_MARGIN * 2 + model.Variable.SIZE,
            'type': 'list'
        })

        # variables
        for i, json in enumerate([{key: val for key, val in var.items() if key != 'pyobj'} for var in objs['alist'].export()['vars']]):
            self.assertEqual(json, {
                'x': x + model.StdCollection.H_MARGIN + model.Variable.SIZE * i,
                'y': y + model.StdCollection.V_MARGIN,
                'width': model.Variable.SIZE,
                'height': model.Variable.SIZE,
                'name': f'{i}',
            })

        # ints the variables point to
        for i, json in enumerate([var['pyobj'] for var in objs['alist'].export()['vars']]):
            self.assertEqual(json, {
                'x': 0,
                'y': 0,
                'width': model.Value.RADIUS * 2,
                'height': model.Value.RADIUS * 2,
                'type': 'int',
                'text': f'{i + 1}'
            })

    def test_basic_instance(self):
        class H:
            hi = 5

            def high5():
                pass

        objs, _ = self.make_models(locals())

        x, y = (30, 35)
        objs['H'].set_xy(x, y)
        namespace = objs['H'].get_namespace()
        fx, fy = (40, 45)

        for var in namespace.get_variables():
            if var.get_name() == 'high5':
                var.get_pyobj().set_pos(fx, fy)

        # instance
        self.assertEqual({key: val for key, val in objs['H'].export().items() if key != 'namespace'}, {
            'x': x,
            'y': y,
            'width': model.Instance.H_MARGIN * 2 + namespace.get_width(),
            'height': model.Instance.V_MARGIN * 2 + namespace.get_height(),
            'type': 'type'
        })

        # namespace
        self.assertEqual({key: val for key, val in namespace.export().items() if key != 'vars'}, {
            'x': x + model.Instance.H_MARGIN,
            'y': y + model.Instance.V_MARGIN,
            'width': model.Namespace.H_MARGIN * 2 + model.Variable.SIZE,
            'height': model.Namespace.V_MARGIN * 2 + model.Variable.SIZE * len(namespace.get_obj()) + model.Namespace.VAR_GAP * (len(namespace.get_obj()) - 1),
            'type': 'dict'
        })

        # variables
        for i, json in enumerate([{key: val for key, val in var.items() if key != 'pyobj' and key != 'name'} for var in namespace.export()['vars']]):
            self.assertEqual(json, {
                'x': x + model.Instance.H_MARGIN + model.Namespace.H_MARGIN,
                'y': y + model.Instance.V_MARGIN + model.Namespace.V_MARGIN + (model.Variable.SIZE + model.Namespace.VAR_GAP) * i,
                'width': model.Variable.SIZE,
                'height': model.Variable.SIZE,
            })

        self.assertEqual({var['name'] for var in namespace.export()['vars']}, {
            'hi', 'high5'
        })

        # values the variables point to
        for var in namespace.export()['vars']:
            if var['name'] == 'hi':
                self.assertEqual(var['pyobj'], {
                    'x': 0,
                    'y': 0,
                    'width': model.Value.RADIUS * 2,
                    'height': model.Value.RADIUS * 2,
                    'type': 'int',
                    'text': '5'
                })
            elif var['name'] == 'high5':
                self.assertEqual(var['pyobj'], {
                    'x': fx,
                    'y': fy,
                    'width': model.Instance.H_MARGIN * 2 + model.Namespace.H_MARGIN * 2,
                    'height': model.Instance.V_MARGIN * 2 + model.Namespace.V_MARGIN * 2,
                    'type': 'function',
                    'namespace': {
                        'x': fx + model.Instance.H_MARGIN,
                        'y': fy + model.Instance.V_MARGIN,
                        'width': model.Namespace.H_MARGIN * 2,
                        'height': model.Namespace.V_MARGIN * 2,
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

    def test_empty_stdcollection(self):
        '''note: an empty namespace is already tested in test_basic_instance'''
        alist = []

        objs, _ = self.make_models(locals())

        self.assertEqual(objs['alist'].export(), {
            'x': 0,
            'y': 0,
            'width': model.StdCollection.H_MARGIN * 2,
            'height': model.StdCollection.V_MARGIN * 2,
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

    def test_set_pospos(self):
        '''this is just to test if the variations on set_x and set_y work since set_x and set_y may be overridden'''
        alist = [1, 2, 3]

        objs, _ = self.make_models(locals())

        # set_x
        x = 10
        objs['alist'].set_x(x)
        self.assertEqual(objs['alist'].export()['x'], x)

        for i, var in enumerate(objs['alist'].get_variables()):
            self.assertEqual(var.export()['x'], x + model.StdCollection.H_MARGIN + model.Variable.SIZE * i)

        # set_y
        y = 15
        objs['alist'].set_y(y)
        self.assertEqual(objs['alist'].export()['y'], y)

        for i, var in enumerate(objs['alist'].get_variables()):
            self.assertEqual(var.export()['y'], y + model.StdCollection.V_MARGIN)

        # set_pos
        x, y = 20, 25
        objs['alist'].set_pos(x, y)
        self.assertEqual(objs['alist'].export()['x'], x)
        self.assertEqual(objs['alist'].export()['y'], y)

        for i, var in enumerate(objs['alist'].get_variables()):
            self.assertEqual(var.export()['x'], x + model.StdCollection.H_MARGIN + model.Variable.SIZE * i)
            self.assertEqual(var.export()['y'], y + model.StdCollection.V_MARGIN)

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
        result_basic = diagrammer._run_code(self.code_sample_basic, self.flags_basic)
        self.assertEqual([self.snapshot_as_vardict(snapshot) for snapshot in result_basic], [
            {
                'globals' : {'x' : '1', 'y' : '2'},
                'locals' : {'x' : '1', 'y' : '2'}
            }
        ])

        result_conditional = diagrammer._run_code(self.code_sample_conditional, self.flags_medium)
        self.assertEqual([self.snapshot_as_vardict(snapshot) for snapshot in result_conditional], [
            {
                'globals' : {'x' : '1', 'b' : '1'},
                'locals' : {'x' : '1', 'b' : '1'}
            }
        ])

        result_loop = diagrammer._run_code(self.code_sample_loop, self.flags_advanced)
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
            'globals' : {var.get_name() : var.get_pyobj().get_text() for var in snapshot._globals._variables},
            'locals' : {var.get_name() : var.get_pyobj().get_text() for var in snapshot._locals._variables},
        }


if __name__ == '__main__':
    unittest.main()
