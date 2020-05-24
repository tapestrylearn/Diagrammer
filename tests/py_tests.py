import utils
utils.setup_pythonpath_for_tests()

import unittest
from diagrammer.python import scene

class PythonBLDToPyConstructTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_basic_values(self):
        myscene = scene.PyScene()

        bld_int = {'id': 0, 'type_str': 'int', 'val': '5'}
        bval = myscene.create_value(bld_int)
        self.assertEqual(bval.get_header(), 'int')
        self.assertEqual(bval.get_content(), '5')

        bld_str = {'id': 1, 'type_str': 'str', 'val': "'hello world'"}
        bval = myscene.create_value(bld_str)
        self.assertEqual(bval.get_header(), 'str')
        self.assertEqual(bval.get_content(), "'hello world'")

        bld_float = {'id': 2, 'type_str': 'float', 'val': '5.5'}
        bval = myscene.create_value(bld_float)
        self.assertEqual(bval.get_header(), 'float')
        self.assertEqual(bval.get_content(), '5.5')

        bld_bool = {'id': 3, 'type_str': 'bool', 'val': 'True'}
        bval = myscene.create_value(bld_bool)
        self.assertEqual(bval.get_header(), 'bool')
        self.assertEqual(bval.get_content(), 'True')

        bld_func = {'id': 4, 'type_str': 'function', 'val': '...'}
        bval = myscene.create_value(bld_func)
        self.assertEqual(bval.get_header(), 'function')
        self.assertEqual(bval.get_content(), '...')

        bld_none = {'id': 5, 'type_str': 'NoneType', 'val': 'None'}
        bval = myscene.create_value(bld_none)
        self.assertEqual(bval.get_header(), 'NoneType')
        self.assertEqual(bval.get_content(), 'None')

        # TODO: add testing erroneous objitives

    def test_collections(self):
        myscene = scene.PyScene()

        # list
        bld_list = {
            'id': 0,
            'type_str': 'list',
            'val': [
                {'id': 1, 'type_str': 'int', 'val': '2'},
                {'id': 2, 'type_str': 'str', 'val': "'hi'"},
                {'id': 3, 'type_str': 'bool', 'val': 'False'}
            ]
        }

        col = myscene.create_value(bld_list)
        self.assertEqual(col.get_header(), 'list')
        self.assertEqual([var.get_header() for var in col.get_contents()], ['0', '1', '2'])
        self.assertEqual([var.get_content() for var in col.get_contents()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_contents()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_contents()], ['2', "'hi'", 'False'])

        # tuple
        bld_tuple = {
            'id': 4,
            'type_str': 'tuple',
            'val': [
                {'id': 5, 'type_str': 'int', 'val': '2'},
                {'id': 6, 'type_str': 'str', 'val': "'hi'"},
                {'id': 7, 'type_str': 'bool', 'val': 'False'}
            ]
        }

        col = myscene.create_value(bld_tuple)
        self.assertEqual(col.get_header(), 'tuple')
        self.assertEqual([var.get_header() for var in col.get_contents()], ['0', '1', '2'])
        self.assertEqual([var.get_content() for var in col.get_contents()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_contents()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_contents()], ['2', "'hi'", 'False'])

        # set
        bld_set = {
            'id': 8,
            'type_str': 'set',
            'val': [
                {'id': 9, 'type_str': 'int', 'val': '2'},
                {'id': 10, 'type_str': 'str', 'val': "'hi'"},
                {'id': 11, 'type_str': 'bool', 'val': 'False'}
            ]
        }

        col = myscene.create_value(bld_set)
        self.assertEqual(col.get_header(), 'set')
        self.assertEqual([var.get_header() for var in col.get_contents()], ['', '', ''])
        self.assertEqual([var.get_content() for var in col.get_contents()], ['', '', ''])
        self.assertEqual([var.get_head_obj().get_header() for var in col.get_contents()], ['int', 'str', 'bool'])
        self.assertEqual([var.get_head_obj().get_content() for var in col.get_contents()], ['2', "'hi'", 'False'])

        # dict
        bld_dict = {
            'id': 12,
            'type_str': 'dict',
            'val': {
                'tap': {'id': 13, 'type_str': 'int', 'val': '2'},
                'es': {'id': 14, 'type_str': 'str', 'val': "'hi'"},
                'try': {'id': 15, 'type_str': 'bool', 'val': 'False'}
            }
        }

        col = myscene.create_value(bld_dict)
        self.assertEqual(col.get_header(), 'dict')
        self.assertEqual({var.get_header() for var in col.get_contents()}, {'tap', 'es', 'try'})
        self.assertEqual({var.get_content() for var in col.get_contents()}, {'', '', ''})
        self.assertEqual({var.get_head_obj().get_header() for var in col.get_contents()}, {'int', 'str', 'bool'})
        self.assertEqual({var.get_head_obj().get_content() for var in col.get_contents()}, {'2', "'hi'", 'False'})

        # TODO: add testing erroneous collections

    '''def test_objects(self):
        # standard object
        bld_bval = {
            'id': 0,
            'type_str': 'A',
            'val': {
                'id': 1,
                'type_str': 'dict',
                'val': {
                    'high': {'id': 2, 'type_str': 'str', 'val': "'five'"},
                    'team': {'id': 3, 'type_str': 'int', 'val': '10'},
                    'oh_shit_thats': {'id': 4, 'type_str': 'bool', 'val': 'True'}
                }
            }
        }

        bval = scene.PyObject(bld_obj)
        self.assertEqual(bval.get_header(), 'A')
        self.assertEqual(bval.get_content(), '')
        self.assertEqual(bval.get_col().get_header(), 'dict')
        self.assertEqual(bval.get_col().get_content(), '')
        self.assertEqual(bval.get_col().get_sections().keys(), {'attrs'})
        self.assertEqual(bval.get_col().get_section_order(), ['attrs'])
        self.assertEqual(bval.get_col().get_section_reorderable(), False)
        self.assertTrue(all([len(var_group) == 1 for var_group in bval.get_col().get_sections()['attrs']]))
        self.assertEqual({var_group[0].get_header() for var_group in bval.get_col().get_sections()['attrs']}, {'high', 'team', 'oh_shit_thats'})
        self.assertEqual({var_group[0].get_content() for var_group in bval.get_col().get_sections()['attrs']}, {''})
        self.assertEqual({var_group[0].get_head_obj().get_header() for var_group in bval.get_col().get_sections()['attrs']}, {'int', 'str', 'bool'})
        self.assertEqual({var_group[0].get_head_obj().get_content() for var_group in bval.get_col().get_sections()['attrs']}, {"'five'", '10', 'True'})

        # TODO: add testing erroneous object

    def test_classes(self):
        # standard class
        # TODO: figure out the ???'s in the specification
        bld_class = {
            'id': 0,
            'type_str': 'type',
            'val': {
                'id': 1,
                'type_str': 'mappingproxy',
                'val': {
                    '__module__': {'id': 2, 'type_str': 'str', 'val': "'__main__'"},
                    '__dict__': {'id': 3, 'type_str': 'str', 'val': "'???'"},
                    '__weakref__': {'id': 4, 'type_str': 'str', 'val': "'???'"},
                    '__doc__': {'id': 5, 'type_str': 'NoneType', 'val': 'None'},
                    'STATIC_INT': {'id': 6, 'type_str': 'int', 'val': '5'},
                    'hi': {'id': 7, 'type_str': 'function', 'val': '...'}
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
        self.assertEqual({var_group[0].get_header() for var_group in clss.get_col().get_sections()['attrs']}, {'STATIC_INT'})
        self.assertEqual({var_group[0].get_content() for var_group in clss.get_col().get_sections()['attrs']}, {''})
        self.assertEqual({var_group[0].get_head_obj().get_header() for var_group in clss.get_col().get_sections()['attrs']}, {'int'})
        self.assertEqual({var_group[0].get_head_obj().get_content() for var_group in clss.get_col().get_sections()['attrs']}, {'5'})
        self.assertTrue(all([len(var_group) == 1 for var_group in clss.get_col().get_sections()['methods']]))
        self.assertEqual({var_group[0].get_header() for var_group in clss.get_col().get_sections()['methods']}, {'hi'})
        self.assertEqual({var_group[0].get_content() for var_group in clss.get_col().get_sections()['methods']}, {''})
        self.assertEqual({var_group[0].get_head_obj().get_header() for var_group in clss.get_col().get_sections()['methods']}, {'function'})
        self.assertEqual({var_group[0].get_head_obj().get_content() for var_group in clss.get_col().get_sections()['methods']}, {'...'})

        # classes with hidden vars
        clss = scene.PyClass(bld_class, show_class_hidden_vars = True)
        self.assertEqual(clss.get_col().get_sections().keys(), {'hidden', 'attrs', 'methods'})
        self.assertEqual(clss.get_col().get_section_order(), ['hidden', 'attrs', 'methods'])
        self.assertEqual(clss.get_col().get_section_reorderable(), False)
        self.assertTrue(all([len(var_group) == 1 for var_group in clss.get_col().get_sections()['hidden']]))
        self.assertEqual({var_group[0].get_header() for var_group in clss.get_col().get_sections()['hidden']}, {'__module__', '__weakref__', '__doc__', '__dict__'})

        # TODO: add testing erroneous classes

    def test_scene(self):
        bld_scene = {
            'a': {'id': 0, 'type_str': 'int', 'val': '5'},
            'b': {'id': 1, 'type_str': 'str', 'val': "'hi'"}
        }

        scne = scene.PyScene(bld_scene)
        self.assertEqual({bval.get_header() for obj in scne.get_objs()}, {'a', 'b'})
        self.assertEqual({bval.get_content() for obj in scne.get_objs()}, {'', ''})
        self.assertEqual({bval.get_head_obj().get_header() for obj in scne.get_objs()}, {'int', 'str'})
        self.assertEqual({bval.get_head_obj().get_content() for obj in scne.get_objs()}, {'5', "'hi'"})

    def test_snapshot(self):
        bld_globals = {
            'HI': {'id': 0, 'type_str': 'int', 'val': '5'},
            'HELLO': {'id': 1, 'type_str': 'str', 'val': "'yellow'"}
        }

        bld_locals = {
            'a': {'id': 0, 'type_str': 'int', 'val': '5'},
            'b': {'id': 1, 'type_str': 'str', 'val': "'hi'"}
        }

        snap = scene.PySnapshot(bld_globals, bld_locals)
        self.assertEqual({bval.get_header() for obj in snap.get_scene('globals').get_objs()}, {'HI', 'HELLO'})
        self.assertEqual({bval.get_header() for obj in snap.get_scene('locals').get_objs()}, {'a', 'b'})'''


if __name__ == '__main__':
    unittest.main()
