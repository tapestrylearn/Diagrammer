import utils
utils.setup_pythonpath_for_tests()

import unittest
from diagrammer.python import scene

class PythonBLDToPyConstructTests(unittest.TestCase):
    def setUp(self):
        self._int_bld = {'id': 0, 'type_str': 'int', 'val': '5'}
        self._str_bld = {'id': 1, 'type_str': 'str', 'val': "'hello world'"}
        self._float_bld = {'id': 2, 'type_str': 'float', 'val': '5.5'}
        self._bool_bld = {'id': 3, 'type_str': 'bool', 'val': 'True'}
        self._func_bld = {'id': 4, 'type_str': 'function', 'val': '...'}
        self._none_bld = {'id': 5, 'type_str': 'NoneType', 'val': 'None'}

        self._list_bld = {
            'id': 6,
            'type_str': 'list',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        self._tuple_bld = {
            'id': 7,
            'type_str': 'tuple',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        self._set_bld = {
            'id': 8,
            'type_str': 'set',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        self._dict_bld = {
            'id': 9,
            'type_str': 'dict',
            'val': {
                'i': self._int_bld,
                's': self._str_bld,
                'f': self._float_bld
            }
        }

        self._obj_bld = {
            'id': 10,
            'type_str': 'A',
            'val': {
                'id': 11,
                'type_str': 'dict',
                'obj_type': 'obj',
                'val': {
                    'high': {'id': 12, 'type_str': 'str', 'val': "'five'"},
                    'team': {'id': 13, 'type_str': 'int', 'val': '10'},
                    'oh_shit_thats': {'id': 14, 'type_str': 'bool', 'val': 'True'}
                }
            }
        }

        self._scene = scene.PyScene()

    def test_basic_value_int_creation(self):
        int_value = self._scene.create_value(self._int_bld)
        self.assertEqual(int_value.get_header(), self._int_bld['type_str'])
        self.assertEqual(int_value.get_content(), self._int_bld['val'])

    def test_basic_value_str_creation(self):
        str_value = self._scene.create_value(self._str_bld)
        self.assertEqual(str_value.get_header(), self._str_bld['type_str'])
        self.assertEqual(str_value.get_content(), self._str_bld['val'])

    def test_basic_value_float_creation(self):
        float_value = self._scene.create_value(self._float_bld)
        self.assertEqual(float_value.get_header(), self._float_bld['type_str'])
        self.assertEqual(float_value.get_content(), self._float_bld['val'])

    def test_basic_value_bool_creation(self):
        bool_value = self._scene.create_value(self._bool_bld)
        self.assertEqual(bool_value.get_header(), self._bool_bld['type_str'])
        self.assertEqual(bool_value.get_content(), self._bool_bld['val'])

    def test_basic_value_func_creation(self):
        func_value = self._scene.create_value(self._func_bld)
        self.assertEqual(func_value.get_header(), self._func_bld['type_str'])
        self.assertEqual(func_value.get_content(), self._func_bld['val'])

    def test_basic_value_none_creation(self):
        none_value = self._scene.create_value(self._none_bld)
        self.assertEqual(none_value.get_header(), self._none_bld['type_str'])
        self.assertEqual(none_value.get_content(), self._none_bld['val'])

        # TODO: add testing erroneous objitives

    def test_collection_list_creation(self):
        list_collection = self._scene.create_value(self._list_bld)

        self.assertEqual(list_collection.get_header(), 'list')

        self.assertEqual([var.get_header() for var in list_collection.get_contents()],
            [f'{index}' for index in range(len(self._list_bld['val']))]
        )

        self.assertEqual(
            [var.get_content() for var in list_collection.get_contents()],
            [''] * len(self._dict_bld['val'])
        )

        self.assertEqual(
            [var.get_head_obj().get_header() for var in list_collection.get_contents()],
            [value_data['type_str'] for value_data in self._list_bld['val']]
        )

        self.assertEqual(
            [var.get_head_obj().get_content() for var in list_collection.get_contents()],
            [value_data['val'] for value_data in self._list_bld['val']]
        )

    def test_collection_tuple_creation(self):
        tuple_collection = self._scene.create_value(self._tuple_bld)

        self.assertEqual(tuple_collection.get_header(), 'tuple')

        self.assertEqual([var.get_header() for var in tuple_collection.get_contents()],
            [f'{index}' for index in range(len(self._tuple_bld['val']))]
        )

        self.assertEqual(
            [var.get_content() for var in tuple_collection.get_contents()],
            [''] * len(self._dict_bld['val'])
        )

        self.assertEqual(
            [var.get_head_obj().get_header() for var in tuple_collection.get_contents()],
            [value_data['type_str'] for value_data in self._tuple_bld['val']]
        )

        self.assertEqual(
            [var.get_head_obj().get_content() for var in tuple_collection.get_contents()],
            [value_data['val'] for value_data in self._tuple_bld['val']]
        )

    def test_collection_set_creation(self):
        set_collection = self._scene.create_value(self._set_bld)

        self.assertEqual(set_collection.get_header(), 'set')

        self.assertEqual([var.get_header() for var in set_collection.get_contents()],
            ['' for index in range(len(self._set_bld['val']))]
        )

        self.assertEqual(
            [var.get_content() for var in set_collection.get_contents()],
            [''] * len(self._dict_bld['val'])
        )

        self.assertEqual(
            [var.get_head_obj().get_header() for var in set_collection.get_contents()],
            [value_data['type_str'] for value_data in self._set_bld['val']]
        )

        self.assertEqual(
            [var.get_head_obj().get_content() for var in set_collection.get_contents()],
            [value_data['val'] for value_data in self._set_bld['val']]
        )

    def test_collection_dict_creation(self):
        dict_collection = self._scene.create_value(self._dict_bld)

        self.assertEqual(dict_collection.get_header(), 'dict')
        self.assertEqual(dict_collection.get_content(), '')

        self.assertEqual([var.get_header() for var in dict_collection.get_contents()],
            list(self._dict_bld['val'])
        )

        self.assertEqual(
            [var.get_content() for var in dict_collection.get_contents()],
            [''] * len(self._dict_bld['val'])
        )

        self.assertEqual(
            [var.get_head_obj().get_header() for var in dict_collection.get_contents()],
            [value_data['type_str'] for value_data in self._dict_bld['val'].values()]
        )

        self.assertEqual(
            [var.get_head_obj().get_content() for var in dict_collection.get_contents()],
            [value_data['val'] for value_data in self._dict_bld['val'].values()]
        )

        # TODO: add testing erroneous collections

    def test_collection_contents_set_pos(self):
        pass

    def test_objects(self):
        # standard object
        obj = self._scene.create_value(self._obj_bld)
        self.assertEqual(obj.get_header(), 'A')
        self.assertEqual(obj.get_content(), '')
        self.assertEqual(obj.get_col().get_header(), 'dict')
        self.assertEqual(obj.get_col().get_contents().get_sections().keys(), {'attrs'})
        self.assertEqual(obj.get_col().get_contents().get_section_order(), ['attrs'])
        self.assertEqual({var.get_header() for var in obj.get_col().get_contents()['attrs']}, {'high', 'team', 'oh_shit_thats'})
        self.assertEqual({var.get_content() for var in obj.get_col().get_contents()['attrs']}, {''})
        self.assertEqual({var.get_head_obj().get_header() for var in obj.get_col().get_contents()['attrs']}, {'int', 'str', 'bool'})
        self.assertEqual({var.get_head_obj().get_content() for var in obj.get_col().get_contents()['attrs']}, {"'five'", '10', 'True'})

        # TODO: add testing erroneous object

    '''def test_classes(self):
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
