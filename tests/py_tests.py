import utils
utils.setup_pythonpath_for_tests()

import unittest
from diagrammer.python import scene

class PythonBLDToPyConstructTests(unittest.TestCase):
    def setUp(self):
        self.int_data = {'id': 0, 'type_str': 'int', 'val': '5'}
        self.str_data = {'id': 1, 'type_str': 'str', 'val': "'hello world'"}
        self.float_data = {'id': 2, 'type_str': 'float', 'val': '5.5'}
        self.bool_data = {'id': 3, 'type_str': 'bool', 'val': 'True'}
        self.func_data = {'id': 4, 'type_str': 'function', 'val': '...'}
        self.none_data = {'id': 5, 'type_str': 'NoneType', 'val': 'None'}

        self.list_data = {
            'id': 6,
            'type_str': 'list',
            'val': [
                self.int_data,
                self.str_data,
                self.float_data,
            ]
        }

        self.tuple_data = {
            'id': 7,
            'type_str': 'tuple',
            'val': [
                self.int_data,
                self.str_data,
                self.float_data,
            ]
        }

        self.set_data = {
            'id': 8,
            'type_str': 'set',
            'val': [
                self.int_data,
                self.str_data,
                self.float_data,
            ]
        }

        self.dict_data = {
            'id': 9,
            'type_str': 'dict',
            'val': {
                'i': self.int_data,
                's': self.str_data,
                'f': self.float_data
            }
        }

        self.scene = scene.PyScene()

    def test_basic_value_int_creation(self):
        int_value = self.scene.create_value(self.int_data)
        self.assertEqual(int_value.get_header(), 'int')
        self.assertEqual(int_value.get_content(), '5')

    def test_basic_value_str_creation(self):
        str_value = self.scene.create_value(self.str_data)
        self.assertEqual(str_value.get_header(), 'str')
        self.assertEqual(str_value.get_content(), "'hello world'")

    def test_basic_value_float_creation(self):
        float_value = self.scene.create_value(self.float_data)
        self.assertEqual(float_value.get_header(), 'float')
        self.assertEqual(float_value.get_content(), '5.5')

    def test_basic_value_bool_creation(self):
        bool_value = self.scene.create_value(self.bool_data)
        self.assertEqual(bool_value.get_header(), 'bool')
        self.assertEqual(bool_value.get_content(), 'True')

    def test_basic_value_func_creation(self):
        func_value = self.scene.create_value(self.func_data)
        self.assertEqual(func_value.get_header(), 'function')
        self.assertEqual(func_value.get_content(), '...')

    def test_basic_value_none_creation(self):
        none_value = self.scene.create_value(self.none_data)
        self.assertEqual(none_value.get_header(), 'NoneType')
        self.assertEqual(none_value.get_content(), 'None')

        # TODO: add testing erroneous objitives

    def test_collection_list_creationn(self):
        list_collection = self.scene.create_value(self.list_data)

        self.assertEqual(list_collection.get_header(), 'list')

        self.assertEqual([var.get_header() for var in list_collection.get_contents()], 
            [f'{index}' for index in range(len(self.list_data['val']))]
        )

        self.assertEqual(
            [var.get_content() for var in list_collection.get_contents()], 
            [''] * len(self.dict_data['val'])
        )

        self.assertEqual(
            [var.get_head_obj().get_header() for var in list_collection.get_contents()], 
            [value_data['type_str'] for value_data in self.list_data['val']]
        )

        self.assertEqual(
            [var.get_head_obj().get_content() for var in list_collection.get_contents()], 
            [value_data['val'] for value_data in self.list_data['val']]
        )

    def test_collection_tuple_creationn(self):
        tuple_collection = self.scene.create_value(self.tuple_data)

        self.assertEqual(tuple_collection.get_header(), 'tuple')

        self.assertEqual([var.get_header() for var in tuple_collection.get_contents()], 
            [f'{index}' for index in range(len(self.tuple_data['val']))]
        )

        self.assertEqual(
            [var.get_content() for var in tuple_collection.get_contents()], 
            [''] * len(self.dict_data['val'])
        )

        self.assertEqual(
            [var.get_head_obj().get_header() for var in tuple_collection.get_contents()], 
            [value_data['type_str'] for value_data in self.tuple_data['val']]
        )

        self.assertEqual(
            [var.get_head_obj().get_content() for var in tuple_collection.get_contents()], 
            [value_data['val'] for value_data in self.tuple_data['val']]
        )

    def test_collection_set_creationn(self):
        set_collection = self.scene.create_value(self.set_data)

        self.assertEqual(set_collection.get_header(), 'set')

        self.assertEqual([var.get_header() for var in set_collection.get_contents()], 
            ['' for index in range(len(self.set_data['val']))]
        )

        self.assertEqual(
            [var.get_content() for var in set_collection.get_contents()], 
            [''] * len(self.dict_data['val'])
        )

        self.assertEqual(
            [var.get_head_obj().get_header() for var in set_collection.get_contents()], 
            [value_data['type_str'] for value_data in self.set_data['val']]
        )

        self.assertEqual(
            [var.get_head_obj().get_content() for var in set_collection.get_contents()], 
            [value_data['val'] for value_data in self.set_data['val']]
        )

    def test_collection_dict_creationn(self):
        dict_collection = self.scene.create_value(self.dict_data)

        self.assertEqual(dict_collection.get_header(), 'dict')

        self.assertEqual([var.get_header() for var in dict_collection.get_contents()], 
            list(self.dict_data['val'])
        )

        self.assertEqual(
            [var.get_content() for var in dict_collection.get_contents()], 
            [''] * len(self.dict_data['val'])
        )

        self.assertEqual(
            [var.get_head_obj().get_header() for var in dict_collection.get_contents()], 
            [value_data['type_str'] for value_data in self.dict_data['val'].values()]
        )

        self.assertEqual(
            [var.get_head_obj().get_content() for var in dict_collection.get_contents()], 
            [value_data['val'] for value_data in self.dict_data['val'].values()]
        )

        # TODO: add testing erroneous collections

    def test_collection_set_pos(self):
        pass

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
