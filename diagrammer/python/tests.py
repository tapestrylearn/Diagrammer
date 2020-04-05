import unittest
import model

class DiagrammerTests(unittest.TestCase):
    def setUp(self):
        # resetting to initial state
        model.PyObject.clear_directory()

    def test_basic_variable_and_value(self):
        anint = 1

        objs, vars = make_models(locals())
        vars['anint'].set_xy(20, 25)
        objs['anint'].set_xy(30, 35)

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

    def test_basic_primitive_collection(self):
        alist = [1, 2, 3]

        objs, _ = make_models(locals())

        x, y = (30, 35)
        objs['alist'].set_xy(x, y)

        # outer layer
        self.assertEqual({key: val for key, val in objs['alist'].export().items() if key != 'vars'}, {
            'x': x,
            'y': y,
            'width': model.PrimitiveCollection.H_MARGIN * 2 + model.Variable.SIZE * len(alist),
            'height': model.PrimitiveCollection.V_MARGIN * 2 + model.Variable.SIZE,
            'type': 'list'
        })

        # variables
        for i, json in enumerate([{key: val for key, val in var.items() if key != 'pyobj'} for var in objs['alist'].export()['vars']]):
            self.assertEqual(json, {
                'x': x + model.PrimitiveCollection.H_MARGIN + model.Variable.SIZE * i,
                'y': y + model.PrimitiveCollection.V_MARGIN,
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

    def test_basic_namespace(self):
        class H:
            hi = 5

            def high5():
                pass

        objs, _ = make_models(locals())

        x, y = (30, 35)
        objs['H'].set_xy(x, y)
        ddict = objs['H'].get_ddict()
        fx, fy = (40, 45)

        for var in ddict.get_variables():
            if var.get_name() == 'high5':
                var.get_pyobj().set_xy(fx, fy)

        # outer namespace
        self.assertEqual({key: val for key, val in objs['H'].export().items() if key != 'ddict'}, {
            'x': x,
            'y': y,
            'width': model.Namespace.H_MARGIN * 2 + ddict.get_width(),
            'height': model.Namespace.V_MARGIN * 2 + ddict.get_height(),
            'type': 'type'
        })

        # outer collection
        self.assertEqual({key: val for key, val in ddict.export().items() if key != 'vars'}, {
            'x': x + model.Namespace.H_MARGIN,
            'y': y + model.Namespace.V_MARGIN,
            'width': model.DDictCollection.H_MARGIN * 2 + model.Variable.SIZE,
            'height': model.DDictCollection.V_MARGIN * 2 + model.Variable.SIZE * len(ddict.get_obj()) + model.DDictCollection.VAR_GAP * (len(ddict.get_obj()) - 1),
            'type': 'dict'
        })

        # variables
        for i, json in enumerate([{key: val for key, val in var.items() if key != 'pyobj' and key != 'name'} for var in ddict.export()['vars']]):
            self.assertEqual(json, {
                'x': x + model.Namespace.H_MARGIN + model.DDictCollection.H_MARGIN,
                'y': y + model.Namespace.V_MARGIN + model.DDictCollection.V_MARGIN + (model.Variable.SIZE + model.DDictCollection.VAR_GAP) * i,
                'width': model.Variable.SIZE,
                'height': model.Variable.SIZE,
            })

        self.assertEqual({var['name'] for var in ddict.export()['vars']}, {
            'hi', 'high5'
        })

        # values the variables point to
        for var in ddict.export()['vars']:
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
                    'width': model.Namespace.H_MARGIN * 2 + model.DDictCollection.H_MARGIN * 2,
                    'height': model.Namespace.V_MARGIN * 2 + model.DDictCollection.V_MARGIN * 2,
                    'type': 'function',
                    'ddict': {
                        'x': fx + model.Namespace.H_MARGIN,
                        'y': fy + model.Namespace.V_MARGIN,
                        'width': model.DDictCollection.H_MARGIN * 2,
                        'height': model.DDictCollection.V_MARGIN * 2,
                        'type': 'dict',
                        'vars': []
                    }
                })

    def test_value_text(self):
        # primitives
        anint = 1
        afloat = 2.5
        abool = True
        astr = 'hello world'
        anone = None

        objs, _ = make_models(locals())

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

        objs, _ = make_models(locals())

        self.assertEqual(objs['range1'].export()['text'], '0:5')
        self.assertEqual(objs['range2'].export()['text'], '1:5')
        self.assertEqual(objs['range3'].export()['text'], '1:5:2')
        self.assertEqual(objs['range3_default'].export()['text'], '1:5')

    def test_empty_primitive_collection(self):
        '''note: an empty ddict_collection is already tested in test_basic_namespace'''
        alist = []

        objs, _ = make_models(locals())

        self.assertEqual(objs['alist'].export(), {
            'x': 0,
            'y': 0,
            'width': model.PrimitiveCollection.H_MARGIN * 2,
            'height': model.PrimitiveCollection.V_MARGIN * 2,
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

        objs, _ = make_models(locals())

        self.assertTrue(objs['anint'] is objs['intcopy'])
        self.assertTrue(objs['anint'] is objs['intsame'])
        self.assertTrue(objs['anint'] is not objs['intdiff'])

        self.assertTrue(objs['alist'] is objs['listcopy'])
        self.assertTrue(objs['alist'] is not objs['listsame'])
        self.assertTrue(objs['alist'] is not objs['listdiff'])

        # simple nested list
        x = [3, 8, 6]
        y = [x, 4, 0]

        objs, vars = make_models(locals())

        self.assertTrue(objs['x'] is objs['y'].get_variables()[0].get_pyobj())
        self.assertTrue(vars['x'] is not objs['y'].get_variables()[0])

        # self-referential list
        z = [7, 8, 5]
        z[0] = z

        x = [3, 8, 6]
        y = [x, 4, 0]
        x[2] = y

        objs, vars = make_models(locals())

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
        a.my_ddict = a.__dict__

        objs, vars = make_models(locals())

        for var in objs['a'].get_ddict().get_variables():
            if var.get_name() == 'my_copy':
                self.assertTrue(objs['a'] is var.get_pyobj())
            elif var.get_name() == 'my_ddict':
                self.assertTrue(var.get_pyobj())

    def test_set_xypos(self):
        '''this is just to test if the variations on set_x and set_y work since set_x and set_y may be overridden'''
        alist = [1, 2, 3]

        objs, _ = make_models(locals())

        # set_x
        x = 10
        objs['alist'].set_x(x)
        self.assertEqual(objs['alist'].export()['x'], x)

        for i, var in enumerate(objs['alist'].get_variables()):
            self.assertEqual(var.export()['x'], x + model.PrimitiveCollection.H_MARGIN + model.Variable.SIZE * i)

        # set_y
        y = 15
        objs['alist'].set_y(y)
        self.assertEqual(objs['alist'].export()['y'], y)

        for i, var in enumerate(objs['alist'].get_variables()):
            self.assertEqual(var.export()['y'], y + model.PrimitiveCollection.V_MARGIN)

        # set_xy
        x, y = 20, 25
        objs['alist'].set_xy(x, y)
        self.assertEqual(objs['alist'].export()['x'], x)
        self.assertEqual(objs['alist'].export()['y'], y)

        for i, var in enumerate(objs['alist'].get_variables()):
            self.assertEqual(var.export()['x'], x + model.PrimitiveCollection.H_MARGIN + model.Variable.SIZE * i)
            self.assertEqual(var.export()['y'], y + model.PrimitiveCollection.V_MARGIN)

        # set_pos
        x, y = (30, 35)

        objs['alist'].set_pos((x, y))
        self.assertEqual(objs['alist'].export()['x'], x)
        self.assertEqual(objs['alist'].export()['y'], y)

        for i, var in enumerate(objs['alist'].get_variables()):
            self.assertEqual(var.export()['x'], x + model.PrimitiveCollection.H_MARGIN + model.Variable.SIZE * i)
            self.assertEqual(var.export()['y'], y + model.PrimitiveCollection.V_MARGIN)


# helper functions
def make_models(this_locals: {str : object}) -> (dict, dict):
    objs = {name : model.PyObject.make_for_obj(obj) for name, obj in this_locals.items() if name != 'self'}
    vars = {name : model.Variable(name, obj) for name, obj in objs.items()}
    return (objs, vars)

if __name__ == '__main__':
    unittest.main()
