import utils
utils.setup_tests()

import unittest
from diagrammer.python import scene

class DiagrammerPythonSceneTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        scene.PyFactory.clear_directory()

    def test_primitives(self):
        bld_int = {'id': 0, 'typestr': 'int', 'val': 5}
        prim = scene.PyPrimitive(bld_int)
        self.assertEqual(prim.get_header(), 'int')
        self.assertEqual(prim.get_content(), '5')

        bld_str = {'id': 0, 'typestr': 'str', 'val': 'hello world'}
        prim = scene.PyPrimitive(bld_str)
        self.assertEqual(prim.get_header(), 'str')
        self.assertEqual(prim.get_content(), "'hello world'")

        bld_float = {'id': 0, 'typestr': 'float', 'val': 5.5}
        prim = scene.PyPrimitive(bld_float)
        self.assertEqual(prim.get_header(), 'float')
        self.assertEqual(prim.get_content(), '5.5')

        bld_bool = {'id': 0, 'typestr': 'bool', 'val': True}
        prim = scene.PyPrimitive(bld_bool)
        self.assertEqual(prim.get_header(), 'bool')
        self.assertEqual(prim.get_content(), 'True')

        # TODO: add None and function

        # TODO: add testing erroneous primitives

    def test_collections(self):
        # list
        bld_list = {
            'id': 0,
            'typestr': 'list',
            'val': [
                {'id': 1, 'typestr': 'int', 'val': 2},
                {'id': 2, 'typestr': 'str', 'val': 'hi'},
                {'id': 5, 'typestr': 'bool', 'val': False}
            ]
        }

        col = scene.PyCollection(bld_list)
        self.assertEqual(col.get_header(), 'list')
        self.assertEqual(col.get_content(), '')
        self.assertEqual([var.get_header() for var in col.get_vars()], ['0', '1', '2'])
        self.assertEqual([var.get_content() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_vars()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_vars()], ['2', "'hi'", 'False'])

        # tuple
        bld_tuple = {
            'id': 0,
            'typestr': 'tuple',
            'val': [
                {'id': 1, 'typestr': 'int', 'val': 2},
                {'id': 2, 'typestr': 'str', 'val': 'hi'},
                {'id': 5, 'typestr': 'bool', 'val': False}
            ]
        }

        col = scene.PyCollection(bld_tuple)
        self.assertEqual(col.get_header(), 'tuple')
        self.assertEqual(col.get_content(), '')
        self.assertEqual([var.get_header() for var in col.get_vars()], ['0', '1', '2'])
        self.assertEqual([var.get_content() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_vars()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_vars()], ['2', "'hi'", 'False'])

        # set
        bld_set = {
            'id': 0,
            'typestr': 'set',
            'val': [
                {'id': 1, 'typestr': 'int', 'val': 2},
                {'id': 2, 'typestr': 'str', 'val': 'hi'},
                {'id': 5, 'typestr': 'bool', 'val': False}
            ]
        }

        col = scene.PyCollection(bld_set)
        self.assertEqual(col.get_header(), 'set')
        self.assertEqual(col.get_content(), '')
        self.assertEqual([var.get_header() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_content() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_vars()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_vars()], ['2', "'hi'", 'False'])

        # dict
        bld_dict = {
            'id': 0,
            'typestr': 'dict',
            'val': {
                'tap': {'id': 1, 'typestr': 'int', 'val': 2},
                'es': {'id': 2, 'typestr': 'str', 'val': 'hi'},
                'try': {'id': 5, 'typestr': 'bool', 'val': False}
            }
        }

        col = scene.PyCollection(bld_dict)
        self.assertEqual(col.get_header(), 'dict')
        self.assertEqual(col.get_content(), '')
        self.assertEqual([var.get_header() for var in col.get_vars()], ['tap', 'es', 'try'])
        self.assertEqual([var.get_content() for var in col.get_vars()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_vars()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_vars()], ['2', "'hi'", 'False'])

        # TODO: add testing erroneous collections

    def test_classes(self):
        # standard class
        # TODO: figure out the ???'s
        bld_class = {
            'id': 0,
            'typestr': 'type',
            'val': {
                '__dict__': {
                    'id': 1,
                    'typestr': 'mappingproxy',
                    'val': {
                        '__module__': {'id': 2, 'typestr': 'str', 'val': '__main__'},
                        '__dict__': {'id': 3, 'typestr': 'str', 'val': '???'},
                        '__weakref__': {'id': 4, 'typestr': 'str', 'val': '???'},
                        '__doc__': {'id': 5, 'typestr': 'NoneType', 'val': 'None'},
                        'STATIC_INT': {'id': 6, 'typestr': 'int', 'val': 5},
                        'hi': {'id': 7, 'typestr': 'function', 'val': '...'}
                    }
                }
            }
        }

        clss = scene.PyClass(bld_class)
        self.assertEqual(clss.get_header(), 'type')
        self.assertEqual(clss.get_content(), '')
        self.assertEqual(clss.get_col().get_header(), 'mappingproxy')
        self.assertEqual(clss.get_col().get_content(), '')
        self.assertEqual(clss.get_col().get_sections().keys(), {'attrs', 'methods'})
        self.assertEqual(clss.get_col().get_section_order(), ['attrs', 'methods'])
        self.assertEqual(clss.get_col().get_section_reorderable(), False)
        self.assertTrue(all([len(var_group) == 1 for var_group in clss.get_col().get_sections()['attrs']]))
        self.assertEqual([var_group[0].get_header() for var_group in clss.get_col().get_sections()['attrs']], ['STATIC_INT'])
        self.assertEqual([var_group[0].get_content() for var_group in clss.get_col().get_sections()['attrs']], [''])
        self.assertEqual([var_group[0].get_head_obj().get_header() for var_group in clss.get_col().get_sections()['attrs']], ['int'])
        self.assertEqual([var_group[0].get_head_obj().get_content() for var_group in clss.get_col().get_sections()['attrs']], ['5'])
        self.assertTrue(all([len(var_group) == 1 for var_group in clss.get_col().get_sections()['methods']]))
        self.assertEqual([var_group[0].get_header() for var_group in clss.get_col().get_sections()['methods']], ['hi'])
        self.assertEqual([var_group[0].get_content() for var_group in clss.get_col().get_sections()['methods']], [''])
        self.assertEqual([var_group[0].get_head_obj().get_header() for var_group in clss.get_col().get_sections()['methods']], ['function'])
        self.assertEqual([var_group[0].get_head_obj().get_content() for var_group in clss.get_col().get_sections()['methods']], ['...'])

        # classes with hidden vars
        clss = scene.PyClass(bld_class, show_class_hidden_vars = True)
        self.assertEqual(clss.get_col().get_sections().keys(), {'hidden', 'attrs', 'methods'})
        self.assertEqual(clss.get_col().get_section_order(), ['hidden', 'attrs', 'methods'])
        self.assertEqual(clss.get_col().get_section_reorderable(), False)
        self.assertTrue(all([len(var_group) == 1 for var_group in clss.get_col().get_sections()['hidden']]))
        self.assertEqual({var_group[0].get_header() for var_group in clss.get_col().get_sections()['hidden']}, {'__module__', '__weakref__', '__doc__', '__dict__'})

    def test_erroneous_classes(self):
        pass


if __name__ == '__main__':
    unittest.main()
