import utils
utils.setup_pythonpath_for_tests()

import json
import unittest
from diagrammer.python import scene
import sys
import re


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

        self._counter = Counter()

        self._int_bld = {'id': self._counter.next(), 'type_str': 'int', 'val': '5'}
        self._str_bld = {'id': self._counter.next(), 'type_str': 'str', 'val': "'hello world'"}
        self._float_bld = {'id': self._counter.next(), 'type_str': 'float', 'val': '5.5'}
        self._bool_bld = {'id': self._counter.next(), 'type_str': 'bool', 'val': 'True'}
        self._func_bld = {'id': self._counter.next(), 'type_str': 'function', 'val': '...'}
        self._none_bld = {'id': self._counter.next(), 'type_str': 'NoneType', 'val': 'None'}
        self._twoarg_range_data = {'id' : self._counter.next(), 'type_str' : 'range', 'val' : 'range(0, 5)'}
        self._threearg_range_data = {'id' : self._counter.next(), 'type_str' : 'range', 'val' : 'range(0, 8, 2)'}

        self._list_bld = {
            'id': self._counter.next(),
            'type_str': 'list',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        # this is used for primitive testing. if you change it, you have to change the primitive test as well
        self._mostly_prim_list_bld = {
            'id': self._counter.next(),
            'type_str': 'list',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
                self._bool_bld,
                self._none_bld
            ]
        }

        self._tuple_bld = {
            'id': self._counter.next(),
            'type_str': 'tuple',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        self._set_bld = {
            'id': self._counter.next(),
            'type_str': 'set',
            'val': [
                self._int_bld,
                self._str_bld,
                self._float_bld,
            ]
        }

        self._dict_bld = {
            'id': self._counter.next(),
            'type_str': 'dict',
            'val': {
                'i': self._int_bld,
                's': self._str_bld,
                'f': self._float_bld
            }
        }

        self._obj_bld = {
            'id': self._counter.next(),
            'type_str': 'A',
            'val': {
                'id': self._counter.next(),
                'type_str': 'dict',
                'obj_type': 'obj',
                'val': {
                    'high': {'id': self._counter.next(), 'type_str': 'str', 'val': "'five'"},
                    'team': {'id': self._counter.next(), 'type_str': 'int', 'val': '10'},
                    'oh_shit_thats': {'id': self._counter.next(), 'type_str': 'bool', 'val': 'True'}
                }
            }
        }

        # TODO: figure out the ???'s in the specification
        self._class_bld = {
            'id': self._counter.next(),
            'type_str': 'type',
            'val': {
                'id': self._counter.next(),
                'type_str': 'mappingproxy',
                'obj_type': 'class',
                'val': {
                    '__module__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'__main__'"},
                    '__dict__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'???'"},
                    '__weakref__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'???'"},
                    '__doc__': {'id': self._counter.next(), 'type_str': 'NoneType', 'val': 'None'},
                    'STATIC_INT': {'id': self._counter.next(), 'type_str': 'int', 'val': '5'},
                    'hi': {'id': self._counter.next(), 'type_str': 'function', 'val': '...'}
                }
            }
        }

        ddict_id = 'clss->ddict'

        self._dunder_dict_scene_bld = {
            'clss': {
                'id': self._counter.next(),
                'type_str': 'type',
                'val': {
                    'id': ddict_id,
                    'type_str': 'mappingproxy',
                    'obj_type': 'class',
                    'val': {
                        '__module__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'__main__'"},
                        '__dict__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'???'"},
                        '__weakref__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'???'"},
                        '__doc__': {'id': self._counter.next(), 'type_str': 'NoneType', 'val': 'None'},
                        'STATIC_INT': {'id': self._counter.next(), 'type_str': 'int', 'val': '5'},
                        'hi': {'id': self._counter.next(), 'type_str': 'function', 'val': '...'}
                    }
                }
            },
            'ddict': {
                'id': ddict_id,
                'type_str': 'mappingproxy',
                'obj_type': 'class',
                'val': {
                    '__module__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'__main__'"},
                    '__dict__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'???'"},
                    '__weakref__': {'id': self._counter.next(), 'type_str': 'str', 'val': "'???'"},
                    '__doc__': {'id': self._counter.next(), 'type_str': 'NoneType', 'val': 'None'},
                    'STATIC_INT': {'id': self._counter.next(), 'type_str': 'int', 'val': '5'},
                    'hi': {'id': self._counter.next(), 'type_str': 'function', 'val': '...'}
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

    def test_basic_value_range_creation(self):
        twoarg_range_value = self._scene.create_value(self._twoarg_range_data)
        self.assertEqual(twoarg_range_value.get_header(), self._twoarg_range_data['type_str'])
        self.assertEqual(twoarg_range_value.get_content(), '0:5') # TODO: make expected value 'reactive'

        threearg_range_value = self._scene.create_value(self._threearg_range_data)
        self.assertEqual(threearg_range_value.get_header(), self._threearg_range_data['type_str'])
        self.assertEqual(threearg_range_value.get_content(), '0:8:2') # TODO: make expected value 'reactive'

    def test_primitive(self):
        for prim_bld in [self._int_bld, self._float_bld, self._bool_bld, self._none_bld]:
            self.assertTrue(scene.PyPrimitive.is_primitive(prim_bld))

        self.assertFalse(scene.PyPrimitive.is_primitive(self._str_bld))
        self.assertFalse(scene.PyPrimitive.is_primitive(self._func_bld))

        # change settings
        temp_scene = scene.PyScene(scene.PySceneSettings(primitive_era=True))
        temp_scene.create_variable('intobj', self._int_bld)
        self.assertEqual(len(temp_scene.get_directory()), 1) # one var box
        temp_scene.create_variable('strobj', self._str_bld)
        self.assertEqual(len(temp_scene.get_directory()), 4) # + one var box, one arrow, one circle
        temp_scene.create_variable('listobj', self._mostly_prim_list_bld)
        self.assertEqual(len(temp_scene.get_directory()), 13) # + one var box, one arrow, one rounded rect, another arrow, no circle (cuz str_bld covered), and five var boxes

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

    def test_nested_collection(self):
        # this is created here instead of in __init__ because it's a specific bld, not a general reusable one
        nested_list_bld = {
            'id': self._counter.next(),
            'type_str': 'list',
            'val': [
                self._int_bld,
                self._str_bld,
                {
                    'id': self._counter.next(),
                    'type_str': 'list',
                    'val': [
                        self._float_bld,
                        self._bool_bld
                    ]
                }
            ]
        }

        nested_list = self._scene.create_value(nested_list_bld)

        self.assertEqual(nested_list.get_header(), 'list')

        self.assertEqual(
            [var.get_head_obj().get_header() for var in nested_list.get_contents()],
            ['int', 'str', 'list']
        )

        self.assertEqual(nested_list.get_contents()[2].get_head_obj().get_header(), 'list')

        self.assertEqual(
            [var.get_head_obj().get_header() for var in nested_list.get_contents()[2].get_head_obj().get_contents()],
            ['float', 'bool']
        )

    def test_self_ref_collection(self):
        # this is created here instead of in __init__ because it's a specific bld, not a general reusable one
        single_self_ref_bld = {
            'id': 0,
            'type_str': 'list',
            'val': [
                {
                    'id': 0,
                    'type_str': 'list',
                    'val': None
                }
            ]
        }

        twoway_self_ref_bld = {
            'id': 1,
            'type_str': 'list',
            'val': [
                {
                    'id': 2,
                    'type_str': 'list',
                    'val': [
                        {
                            'id': 1,
                            'type_str': 'list',
                            'val': None
                        }
                    ]
                }
            ]
        }

        obj = self._scene.create_value(single_self_ref_bld)
        self.assertEqual(obj.get_header(), 'list')
        self.assertEqual(obj.get_contents()[0].get_head_obj().get_header(), 'list')
        self.assertEqual(obj.get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_header(), 'list')
        self.assertEqual(obj.get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_header(), 'list')
        self.assertTrue(obj.get_contents()[0].get_head_obj() is obj)

        obj = self._scene.create_value(twoway_self_ref_bld)
        self.assertEqual(obj.get_header(), 'list')
        self.assertEqual(obj.get_contents()[0].get_head_obj().get_header(), 'list')
        self.assertEqual(obj.get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_header(), 'list')
        self.assertEqual(obj.get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_header(), 'list')
        self.assertEqual(obj.get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_contents()[0].get_head_obj().get_header(), 'list')
        self.assertTrue(obj.get_contents()[0].get_head_obj() is not obj)
        self.assertTrue(obj.get_contents()[0].get_head_obj().get_contents()[0].get_head_obj() is obj)

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
        self.assertEqual(len(clss.get_coll().get_contents()['internals']), 0)

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

    def test_dunder_dict(self):
        self._scene.construct(self._dunder_dict_scene_bld)
        clss_obj = [val for val in self._scene.get_directory().values() if type(val) == scene.PyVariable and val.get_header() == 'clss'][0].get_head_obj()
        dd_pointer_obj = [val for val in self._scene.get_directory().values() if type(val) == scene.PyVariable and val.get_header() == 'ddict'][0].get_head_obj()
        self.assertTrue(type(clss_obj) is scene.PyNamespace)
        self.assertTrue(type(dd_pointer_obj) is scene.PyNamespaceCollection)
        self.assertTrue(dd_pointer_obj is clss_obj.get_coll())

    def test_scene(self):
        self._scene.construct(self._scene_bld)
        self.assertEqual({obj.get_header() for obj in self._scene.get_directory().values() if type(obj) != scene.PyReference}, {'a', 'b', 'int', 'str'})
        self.assertEqual({obj.get_content() for obj in self._scene.get_directory().values() if type(obj) != scene.PyReference}, {'', '5', "'hi'"})
        self.assertEqual(len([obj for obj in self._scene.get_directory().values() if type(obj) == scene.PyReference]), 2)

    def test_snapshot(self):
        snap = scene.PySnapshot(self._globals_bld, self._locals_bld, 'hello world', '', scene.PySceneSettings(show_class_internal_vars = True))
        self.assertEqual({obj.get_header() for obj in snap.get_scene('globals').get_directory().values() if type(obj) != scene.PyReference}, {'HI', 'HELLO', 'int', 'str'})
        self.assertEqual({obj.get_header() for obj in snap.get_scene('locals').get_directory().values() if type(obj) != scene.PyReference}, {'a', 'b', 'int', 'str'})
        self.assertEqual(snap.get_output(), 'hello world')
        self.assertEqual(snap._scenes['globals']._scene_settings.show_class_internal_vars, True)
        self.assertEqual(snap._scenes['locals']._scene_settings.show_class_internal_vars, True)


if __name__ == '__main__':
    vrb = 2

    if len(sys.argv) == 2:
        if re.match('^[0-9]+$', sys.argv[1]):
            vrb = int(sys.argv[1])

    unittest.main(argv=sys.argv[:1], verbosity=vrb)
