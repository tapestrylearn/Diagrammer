import unittest
import diagrammer.python.scene as scene

class DiagrammerSceneTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        scene.PyFactory.clear_directory()

    def test_primitives(self):
        bld_int_val = {'id': 0, 'typestr': 'int', 'val': 5}
        prim = scene.PyPrimitive(bld_int_val)
        self.assertEqual(prim.get_header(), 'int')
        self.assertEqual(prim.get_content(), '5')

        bld_str_val = {'id': 0, 'typestr': 'str', 'val': 'hello world'}
        prim = scene.PyPrimitive(bld_str_val)
        self.assertEqual(prim.get_header(), 'str')
        self.assertEqual(prim.get_content(), "'hello world'")

        bld_float_val = {'id': 0, 'typestr': 'float', 'val': 5.5}
        prim = scene.PyPrimitive(bld_float_val)
        self.assertEqual(prim.get_header(), 'float')
        self.assertEqual(prim.get_content(), '5.5')

        bld_int_val = {'id': 0, 'typestr': 'bool', 'val': True}
        prim = scene.PyPrimitive(bld_int_val)
        self.assertEqual(prim.get_header(), 'bool')
        self.assertEqual(prim.get_content(), 'True')

    def test_collections(self):
        # list
        bld_list_val = {
            'id': 0,
            'typestr': 'list',
            'val': [
                {'id': 1, 'typestr': 'int', 'val': 2},
                {'id': 2, 'typestr': 'str', 'val': 'hi'},
                {'id': 5, 'typestr': 'bool', 'val': False}
            ]
        }

        col = scene.PyCollection(bld_list_val)
        self.assertEqual(col.get_header(), 'list')
        self.assertEqual(col.get_content(), '')
        self.assertEqual([var.get_header() for var in col.get_vars()], ['0', '1', '2'])
        self.assertEqual([var.get_content() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_vars()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_vars()], ['2', "'hi'", 'False'])

        # tuple
        bld_tuple_val = {
            'id': 0,
            'typestr': 'tuple',
            'val': [
                {'id': 1, 'typestr': 'int', 'val': 2},
                {'id': 2, 'typestr': 'str', 'val': 'hi'},
                {'id': 5, 'typestr': 'bool', 'val': False}
            ]
        }

        col = scene.PyCollection(bld_tuple_val)
        self.assertEqual(col.get_header(), 'tuple')
        self.assertEqual(col.get_content(), '')
        self.assertEqual([var.get_header() for var in col.get_vars()], ['0', '1', '2'])
        self.assertEqual([var.get_content() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_vars()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_vars()], ['2', "'hi'", 'False'])

        # set
        bld_set_val = {
            'id': 0,
            'typestr': 'set',
            'val': [
                {'id': 1, 'typestr': 'int', 'val': 2},
                {'id': 2, 'typestr': 'str', 'val': 'hi'},
                {'id': 5, 'typestr': 'bool', 'val': False}
            ]
        }

        col = scene.PyCollection(bld_set_val)
        self.assertEqual(col.get_header(), 'set')
        self.assertEqual(col.get_content(), '')
        self.assertEqual([var.get_header() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_content() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_vars()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_vars()], ['2', "'hi'", 'False'])

        # dict
        bld_dict_val = {
            'id': 0,
            'typestr': 'dict',
            'val': {
                'tap': {'id': 1, 'typestr': 'int', 'val': 2},
                'es': {'id': 2, 'typestr': 'str', 'val': 'hi'},
                'try': {'id': 5, 'typestr': 'bool', 'val': False}
            }
        }

        col = scene.PyCollection(bld_dict_val)
        self.assertEqual(col.get_header(), 'dict')
        self.assertEqual(col.get_content(), '')
        self.assertEqual([var.get_header() for var in col.get_vars()], ['tap', 'es', 'try'])
        self.assertEqual([var.get_content() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_vars()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_vars()], ['2', "'hi'", 'False'])


if __name__ == '__main__':
    unittest.main()
