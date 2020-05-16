# notes for meeting: talk about valuefactory and testing export vs object (i think we should test object for language and export for general scene)

from ..scene import basic
from collections import OrderedDict

import types


def is_type(bld_val: 'python bld value', type_obj: type) -> bool:
    if bld_val['type_str'] == type_obj.__name__:
        return True

    try:
        return eval(f"isinstance({bld_val['type_str']}(), {type_obj.__name__})")
    except NameError:
        return False


def value_to_str(type_str: str, val: str) -> str:
    # todo: complex checks for custom value str representations
    return val


class PyValue:
    pass

class PyRvalue(PyValue):
    directory = {}

    def __init__(self, obj_id: int):
        PyRvalue.directory[obj_id] = self

    @staticmethod
    def create_value(bare_language_data: dict) -> 'PyRvalue':
        if bare_language_data['id'] in PyRvalue.directory:
            return PyRvalue.directory[bare_language_data['id']]
        else:
            if PyPrimitive.is_primitive(bare_language_data):
                return PyPrimitive.create_primitive(bare_language_data)
            elif PyCollection.is_collection(bare_language_data):
                return PyCollection.create_collection(bare_language_data)
            elif PyObject.is_object(bare_language_data):
                return PyObject.create_object(bare_language_data)
            elif PyClass.is_class(bare_langauge_data):
                return PyClass.create_class(bare_language_data)
            else:
                return None
    

class PyVariable(basic.BasicShape, PyValue):
    SIZE = 50
    SHAPE = basic.Shapes.SQUARE

    def __init__(self, name: str, head_obj: PyRvalue):
        basic.BasicShape.__init__(self, PyVariable.SIZE, PyVariable.SIZE, name, '')
        self._head_obj = head_obj # TODO: create arrow instead

    @staticmethod
    def create_variable(name: str, value_bare_language_data: dict) -> 'PyVariable':
        value = PyRvalue.create_value(value_bare_language_data)

        return PyVariable(name, value)


class PyPrimitive(basic.BasicShape, PyRvalue):
    RADIUS = 25
    SHAPE = basic.Shapes.CIRCLE

    def __init__(self, obj_id: int, type_str: str, value_str: str):
        PyRvalue.__init__(self, obj_id)
        basic.BasicShape.__init__(self, PyPrimitive.RADIUS * 2, PyPrimitive.RADIUS * 2, type_str, value_str)

    @staticmethod
    def is_primitive(bld_val: 'python bld value'):
        return not (is_collection(bld_val) or is_object(bld_val) or is_class(bld_val))

    @staticmethod
    def create_primitive(bare_language_data: dict) -> 'PyPrimitive':
        return PyPrimitive(
            bare_language_data['id'],
            bare_language_data['type_str'],
            value_to_str(bare_language_data['val'])
        )


class PyCollection(basic.SimpleCollection, PyRvalue):
    ORDERED_COL_SET = basic.CollectionSettings(5, 5, 0, basic.CollectionSettings.HORIZONTAL)
    UNORDERED_COL_SET = basic.CollectionSettings(5, 5, 2, basic.CollectionSettings.HORIZONTAL)

    def __init__(self, obj_id: int, col_set: basic.CollectionSettings, type_str: str, vars: [PyVariable], reorderable: bool):
        PyRvalue.__init__(self, obj_id)
        basic.SimpleCollection.__init__(self, type_str, vars, reorderable, col_set) # TODO: make contents

    @staticmethod
    def is_collection(bld_val: 'python bld value') -> bool:
        return PyCollection.is_ordered_collection(bld_val) or PyCollection.is_unordered_collection(bld_val)

    @staticmethod
    def is_ordered_collection(bld_val: 'python bld value') -> bool:
        types = {list, tuple}
        return any(is_type(bld_val, collection_type) for collection_type in types)

    @staticmethod
    def is_unordered_collection(bld_val: 'python bld value') -> bool:
        types = {set, dict, types.MappingProxyType}
        return any(is_type(bld_val, collection_type) for collection_type in types)

    @staticmethod
    def is_mapping_collection(bare_language_data: dict) -> bool:
        types = {dict, types.MappingProxyType}
        return any(is_type(bld_val, collection_type) for collection_type in types)


    @staticmethod
    def create_collection(bare_language_data: dict) -> 'PyCollection':
        obj_id = bare_language_data['id']
        type_str = bare_language_data['type_str']

        elements = []
        reorderable = False
        settings = None

        if PyCollection.is_ordered_collection(bare_language_data):
            for i, element_data in enumerate(bare_language_data['val']):
                variable = PyVariable.create_variable(f'{i}', element_data)
                elements.append(variable)
        elif PyCollection.is_unordered_collection(bare_language_data):
            reorderable = True

            if PyCollection.is_mapping_collection(bare_language_data):
                for key, value_data in bare_language_data['val'].items():
                    variable = PyVariable.create_variable(key, value_data)
                    elements.append(variable)
            else:
                for element_data in bare_language_data['val']:
                    variable = PyVariable.create_variable('', element_data)
                    elements.append(variable)
        else:
            return None

        return PyCollection(obj_id, settings, type_str, elements, reorderable)


class PyObject(basic.Container, PyRvalue):
    COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 3, basic.CollectionSettings.VERTICAL)
    SECTION_REORDERABLE = False
    SECTION_ORDER = ['attrs']

    def __init__(self, obj_id: int, type_str: str, contents: [PyVariable]):
        PyRvalue.__init__(self, obj_id)

        collection = self._init_contents(self, contents)
        basic.Container.__init__(self, type_str, collection)

    def _init_contents(self, contents: [PyVariable]):
        sections = {
            'attrs' : [contents]
        }

        section_struct = basic.SectionStructure(sections, PyObject.SECTION_ORDER, True, PyObject.SECTION_REORDERABLE)

        return basic.ComplexCollection('', section_struct, PyObject.COLLECTION_SETTINGS)

    @staticmethod
    def is_object(bld_val: 'python bld value'):
        return type(bld_val['val']) == dict and bld_val['val'].keys() == {'id', 'type_str', 'val'} and not PyClass.is_class(bld_val)

    @staticmethod
    def create_object(bare_language_data: dict) -> 'PyObject':
        pass


class PyClass(basic.Container, PyRvalue):
    COL_SET = basic.CollectionSettings(8, 8, 5, basic.CollectionSettings.VERTICAL)
    HIDDEN_VARS = {'__module__', '__dict__', '__weakref__', '__doc__'}
    SECTION_REORDERABLE = False

    def __init__(self, obj_id: int, bld_class: 'python bld class', show_class_hidden_vars = False):
        if not PyClass.is_class(bld_class):
            raise TypeError(f'PyClass.__init__: {bld_class} is not a python bld class')

        PyRvalue.__init__(self, obj_id)

        if not show_class_hidden_vars:
            section_order = ['attrs', 'methods']
        else:
            section_order = ['hidden', 'attrs', 'methods']

        sections = dict()

        for section in section_order:
            sections[section] = list()

        for name, bld_val in bld_class['val']['val'].items():
            if not show_class_hidden_vars and name in PyClass.HIDDEN_VARS:
                continue

            if name in PyClass.HIDDEN_VARS:
                section = 'hidden'
            elif bld_val['type_str'] == 'function':
                section = 'methods'
            else:
                section = 'attrs'

            var = PyVariable(name, bld_val)
            sections[section].append([var])

        col = basic.ComplexCollection(PyClass.COL_SET, bld_class['val']['type_str'], sections, section_order, PyClass.SECTION_REORDERABLE)

        basic.Container.__init__(self, bld_class['type_str'], col)

    @staticmethod
    def is_class(bld_val: 'python bld value'):
        return bld_val['type_str'] == 'type'

    @staticmethod
    def create_class(bare_language_data: dict) -> 'PyClass':
        pass


class PyScene(basic.Scene):
    def gps(self) -> None:
        pass

    @staticmethod
    def create_scene(bare_language_data: dict, settings: 'Some kind of settings class') -> 'PyScene':
        pass


class PySnapshot(basic.Snapshot):
    def __init__(self, globals_bld: 'python bld globals', locals_bld: 'python bld locals', output: str):
        global_scene = PyScene.create_scene(globals_bld)
        local_scene = PyScene.create_scene(locals_bld)

        basic.Snapshot.__init__(self, OrderedDict([('globals', global_scene), ('locals', local_scene)]), output)
