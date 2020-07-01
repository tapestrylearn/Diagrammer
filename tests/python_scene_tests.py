import utils
utils.setup_pythonpath_for_tests()

import json
import unittest
from diagrammer.python import scene


class Counter:
    def __init__(self):
        self._count = 0

    def next(self) -> int:
        last_count = self._count
        self._count += 1
        return last_count


class PythonBLDToPyConstructTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

        counter = Counter()

        self._int_bld = {'id': counter.next(), 'type_str': 'int', 'val': '5'}
        self._str_bld = {'id': counter.next(), 'type_str': 'str', 'val': "'hello world'"}
        self._float_bld = {'id': counter.next(), 'type_str': 'float', 'val': '5.5'}
        self._bool_bld = {'id': counter.next(), 'type_str': 'bool', 'val': 'True'}
        self._func_bld = {'id': counter.next(), 'type_str': 'function', 'val': '...'}
        self._none_bld = {'id': counter.next(), 'type_str': 'NoneType', 'val': 'None'}

        self._list_bld = {
            'id': counter.next(),
            'type_str': 'list',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        self._tuple_bld = {
            'id': counter.next(),
            'type_str': 'tuple',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        self._set_bld = {
            'id': counter.next(),
            'type_str': 'set',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        self._dict_bld = {
            'id': counter.next(),
            'type_str': 'dict',
            'val': {
                'i': self._int_bld,
                's': self._str_bld,
                'f': self._float_bld
            }
        }

        self._obj_bld = {
            'id': counter.next(),
            'type_str': 'A',
            'val': {
                'id': counter.next(),
                'type_str': 'dict',
                'obj_type': 'obj',
                'val': {
                    'high': {'id': counter.next(), 'type_str': 'str', 'val': "'five'"},
                    'team': {'id': counter.next(), 'type_str': 'int', 'val': '10'},
                    'oh_shit_thats': {'id': counter.next(), 'type_str': 'bool', 'val': 'True'}
                }
            }
        }

        # TODO: figure out the ???'s in the specification
        self._class_bld = {
            'id': counter.next(),
            'type_str': 'type',
            'val': {
                'id': counter.next(),
                'type_str': 'mappingproxy',
                'obj_type': 'class',
                'val': {
                    '__module__': {'id': counter.next(), 'type_str': 'str', 'val': "'__main__'"},
                    '__dict__': {'id': counter.next(), 'type_str': 'str', 'val': "'???'"},
                    '__weakref__': {'id': counter.next(), 'type_str': 'str', 'val': "'???'"},
                    '__doc__': {'id': counter.next(), 'type_str': 'NoneType', 'val': 'None'},
                    'STATIC_INT': {'id': counter.next(), 'type_str': 'int', 'val': '5'},
                    'hi': {'id': counter.next(), 'type_str': 'function', 'val': '...'}
                }
            }
        }

        self._scene_bld = {
            'a': {'id': 0, 'type_str': 'int', 'val': '5'},
            'b': {'id': 1, 'type_str': 'str', 'val': "'hi'"}
        }

        self._globals_bld = {
            'HI': {'id': 0, 'type_str': 'int', 'val': '5'},
            'HELLO': {'id': 1, 'type_str': 'str', 'val': "'yellow'"}
        }

        self._locals_bld = {
            'a': {'id': 0, 'type_str': 'int', 'val': '5'},
            'b': {'id': 1, 'type_str': 'str', 'val': "'hi'"}
        }

    def setUp(self):
        self._scene = scene.PyScene(scene.PySceneSettings())

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

    def test_object(self):
        # standard object
        obj = self._scene.create_value(self._obj_bld)

        # test container
        self.assertEqual(obj.get_header(), 'A')
        self.assertEqual(obj.get_content(), '')

        # test collection
        self.assertEqual(obj.get_coll().get_header(), 'dict')
        self.assertEqual(obj.get_coll().get_content(), '')

        # test contents
        self.assertEqual(obj.get_coll().get_contents().get_sections().keys(), {'attrs'})
        self.assertEqual(obj.get_coll().get_contents().get_section_order(), ['attrs'])

        # test variables
        self.assertEqual({var.get_header() for var in obj.get_coll().get_contents()['attrs']}, {'high', 'team', 'oh_shit_thats'})
        self.assertEqual({var.get_content() for var in obj.get_coll().get_contents()['attrs']}, {''})
        self.assertEqual({var.get_head_obj().get_header() for var in obj.get_coll().get_contents()['attrs']}, {'int', 'str', 'bool'})
        self.assertEqual({var.get_head_obj().get_content() for var in obj.get_coll().get_contents()['attrs']}, {"'five'", '10', 'True'})

        # TODO: add testing erroneous object

    def test_class(self):
        clss = self._scene.create_value(self._class_bld)

        # test container
        self.assertEqual(clss.get_header(), 'type')
        self.assertEqual(clss.get_content(), '')

        # test collection
        self.assertEqual(clss.get_coll().get_header(), 'mappingproxy')
        self.assertEqual(clss.get_coll().get_content(), '')

        # test contents
        self.assertEqual(clss.get_coll().get_contents().get_sections().keys(), {'internals', 'attrs', 'methods'})
        self.assertEqual(clss.get_coll().get_contents().get_section_order(), ['internals', 'attrs', 'methods'])

        # test internals
        self.assertEqual({var.get_header() for var in clss.get_coll().get_contents()['internals']}, set())
        self.assertEqual({var.get_content() for var in clss.get_coll().get_contents()['internals']}, set())
        self.assertEqual({var.get_head_obj().get_header() for var in clss.get_coll().get_contents()['internals']}, set())
        self.assertEqual({var.get_head_obj().get_content() for var in clss.get_coll().get_contents()['internals']}, set())

        # test attrs
        self.assertEqual({var.get_header() for var in clss.get_coll().get_contents()['attrs']}, {'STATIC_INT'})
        self.assertEqual({var.get_content() for var in clss.get_coll().get_contents()['attrs']}, {''})
        self.assertEqual({var.get_head_obj().get_header() for var in clss.get_coll().get_contents()['attrs']}, {'int'})
        self.assertEqual({var.get_head_obj().get_content() for var in clss.get_coll().get_contents()['attrs']}, {'5'})

        # test methods
        self.assertEqual({var.get_header() for var in clss.get_coll().get_contents()['methods']}, {'hi'})
        self.assertEqual({var.get_content() for var in clss.get_coll().get_contents()['methods']}, {''})
        self.assertEqual({var.get_head_obj().get_header() for var in clss.get_coll().get_contents()['methods']}, {'function'})
        self.assertEqual({var.get_head_obj().get_content() for var in clss.get_coll().get_contents()['methods']}, {'...'})

    def test_class_with_show_internal_vars(self):
        # change settings
        self._scene._scene_settings.show_class_internal_vars = True
        clss = self._scene.create_value(self._class_bld)

        # test internals
        self.assertEqual({var.get_header() for var in clss.get_coll().get_contents()['internals']}, {'__module__', '__dict__', '__weakref__', '__doc__'})
        self.assertEqual({var.get_content() for var in clss.get_coll().get_contents()['internals']}, {''})
        self.assertEqual({var.get_head_obj().get_header() for var in clss.get_coll().get_contents()['internals']}, {'str', 'NoneType'})
        self.assertEqual({var.get_head_obj().get_content() for var in clss.get_coll().get_contents()['internals']}, {"'__main__'", "'???'", "'???'", 'None'})

    # TODO: add testing erroneous classes

    def test_scene(self):
        self._scene.construct(self._scene_bld)
        self.assertEqual({obj.get_header() for obj in self._scene.get_directory().values() if type(obj) != scene.PyReference}, {'a', 'b', 'int', 'str'})
        self.assertEqual({obj.get_content() for obj in self._scene.get_directory().values() if type(obj) != scene.PyReference}, {'', '5', "'hi'"})
        self.assertEqual(len([obj for obj in self._scene.get_directory().values() if type(obj) == scene.PyReference]), 2)

    def test_snapshot(self):
        snap = scene.PySnapshot(self._globals_bld, self._locals_bld, 'hello world', scene.PySceneSettings(show_class_internal_vars = True))
        self.assertEqual({obj.get_header() for obj in snap.get_scene('globals').get_directory().values() if type(obj) != scene.PyReference}, {'HI', 'HELLO', 'int', 'str'})
        self.assertEqual({obj.get_header() for obj in snap.get_scene('locals').get_directory().values() if type(obj) != scene.PyReference}, {'a', 'b', 'int', 'str'})
        self.assertEqual(snap.get_output(), 'hello world')
        self.assertEqual(snap._scenes['globals']._scene_settings.show_class_internal_vars, True)
        self.assertEqual(snap._scenes['locals']._scene_settings.show_class_internal_vars, True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
