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


class PyConstruct:
    pass


class PyRvalue(PyConstruct):
    pass


class PyVariable(basic.BasicShape, PyConstruct):
    SIZE = 50
    SHAPE = basic.Shapes.SQUARE

    def __init__(self, name: str = None):
        basic.BasicShape.__init__(self, PyVariable.SIZE, PyVariable.SIZE, name, '')

    def construct(self, scene: PyScene, bare_lang_data: dict):
        pass


class PyPointer(basic.Arrow):
    OPTIONS = basic.ArrowOptions(
        basic.ArrowOptions.SOLID,
        basic.ArrowOptions.EDGE,
        basic.ArrowOptions.CENTER
    )

    def __init__(self, head_obj: PyRvalue, tail_obj: PyVariable):
        basic.Arrow.__init__(self, head_obj, tail_obj, PyPointer.OPTIONS)


class PyBasicValue(basic.BasicShape, PyRvalue):
    RADIUS = 25
    SHAPE = basic.Shapes.CIRCLE

    def __init__(self, type_str: str = None, value_str: str = None):
        basic.BasicShape.__init__(self, PyBasicValue.RADIUS * 2, PyBasicValue.RADIUS * 2, type_str, value_str)

    def construct(self, scene: PyScene, bare_lang_data: dict):
        pass

    @staticmethod
    def is_basic_value(bare_lang_data: 'python bld value'):
        return not (PyCollection.is_collection(bare_lang_data) or PyObject.is_object(bare_lang_data) or PyClass.is_class(bare_lang_data))


class PyCollectionContents(basic.CollectionContents):
    def __init__(self, elements: [PyVariable], reorderable: bool):
        self._elements = elements
        self._reorderable = reorderable

    def __len__(self) -> int:
        return len(self._elements)

    def __iter__(self) -> 'iterator':
        return iter(self._elements[:])

    def reorder(self, i: int, j: int):
        if self._reorderable:
            self._elements[i], self._elements[j] = self._elements[j], self._elements[i]
        else:
            raise ReorderException()


class PyCollection(basic.Collection, PyRvalue):
    ORDERED_COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 0, basic.CollectionSettings.HORIZONTAL)
    UNORDERED_COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 2, basic.CollectionSettings.HORIZONTAL)

    def __init__(self, type_str: str = None, elements: [PyVariable] = None, reorderable: bool = None, settings: basic.CollectionSettings = None):
        contents = PyCollectionContents(elements, reorderable) if elements != None and reorderable != None else None
        basic.Collection.__init__(self, type_str, contents, settings)

    def construct(self, scene: PyScene, bare_lang_data: dict):
        pass

    @staticmethod
    def is_collection(bare_lang_data: 'python bld value') -> bool:
        return PyCollection.is_ordered_collection(bare_lang_data) or PyCollection.is_unordered_collection(bare_lang_data)

    @staticmethod
    def is_ordered_collection(bare_lang_data: 'python bld value') -> bool:
        types = {list, tuple}
        return any(is_type(bare_lang_data, collection_type) for collection_type in types)

    @staticmethod
    def is_unordered_collection(bare_lang_data: 'python bld value') -> bool:
        types = {set, dict, types.MappingProxyType}
        return any(is_type(bare_lang_data, collection_type) for collection_type in types)

    @staticmethod
    def is_mapping_collection(bare_lang_data: dict) -> bool:
        types = {dict, types.MappingProxyType}
        return any(is_type(bare_lang_data, collection_type) for collection_type in types)


    @staticmethod
    def create_collection(bare_lang_data: dict) -> 'PyCollection':
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


class PyObjectContents(basic.CollectionContents):
    def __init__(self, sections: [(str, [PyVariable])]):
        self._sections = sections

    def __len__(self) -> int:
        return sum(len(section_contents) for _, section_contents in self._sections)

    def __iter__(self) -> 'iterator':
        def gen_contents():
            for _, section in self._sections:
                for var in section:
                    yield section

        return gen_contents()

    def __getitem__(self, section: str) -> [PyVariable]:
        if type(section) == str:
            for section_name, section_contents in self._sections:
                if section_name == section:
                    return section_contents
        else:
            raise IndexError(f"Can't subscript object of type {type(self)} with index of type {type(section)}")

    def iter_by_section(self) -> 'iterator':
        def gen_sections():
            for section in self._sections:
                yield section

        return gen_sections()

    def sections(self) -> [(str, [PyVariable])]:
        return self._sections

    def reorder(self, i: int, j: int):
        self._sections[i], self._sections[j] = self._sections[j], self._sections[i]

    def reorder_within_section(self, section: str, i: int, j: int):
        self[section][i], self[section][j] = self[section][j], self[section][i]


# NOTE; PyObject & PyClass still in progress
class PyObject(basic.Container, PyRvalue):
    COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 3, basic.CollectionSettings.VERTICAL)
    SECTION_ORDER = ['attrs']

    def __init__(self, type_str: str = None, contents: [PyVariable] = None):
        pass

    def construct(self, scene: PyScene, bare_lang_data: dict):
        pass

    @staticmethod
    def is_object(bare_lang_data: 'python bld value'):
        return type(bare_lang_data['val']) == dict and bare_lang_data['val'].keys() == {'id', 'type_str', 'val'} and not PyClass.is_class(bare_lang_data)


class PyClass(basic.Container, PyRvalue):
    COLLECTION_SETTINGS = basic.CollectionSettings(8, 8, 5, basic.CollectionSettings.VERTICAL)
    INTERNAL_VARS = {'__module__', '__dict__', '__weakref__', '__doc__'}

    def __init__(self, obj_id: int, bld_class: 'python bld class', show_class_hidden_vars = False):
        # if not PyClass.is_class(bld_class):
        #     raise TypeError(f'PyClass.__init__: {bld_class} is not a python bld class')

        # PyRvalue.__init__(self, obj_id)

        # if not show_class_hidden_vars:
        #     section_order = ['attrs', 'methods']
        # else:
        #     section_order = ['hidden', 'attrs', 'methods']

        # sections = dict()

        # for section in section_order:
        #     sections[section] = list()

        # for name, bld_val in bld_class['val']['val'].items():
        #     if not show_class_hidden_vars and name in PyClass.HIDDEN_VARS:
        #         continue

        #     if name in PyClass.HIDDEN_VARS:
        #         section = 'hidden'
        #     elif bld_val['type_str'] == 'function':
        #         section = 'methods'
        #     else:
        #         section = 'attrs'

        #     var = PyVariable(name, bld_val)
        #     sections[section].append([var])

        # col = basic.ComplexCollection(PyClass.COL_SET, bld_class['val']['type_str'], sections, section_order, PyClass.SECTION_REORDERABLE)

        # basic.Container.__init__(self, bld_class['type_str'], col)
        pass

    def construct(self, scene: PyScene, bare_lang_data: dict):
        pass

    @staticmethod
    def is_class(bld_val: 'python bld value'):
        return bld_val['type_str'] == 'type'


class PyScene(basic.Scene):
    def __init__(self, bare_lang_data: dict): # TODO: add settings
        # basic.Scene.__init__(self)
        # create scene contents
        pass

    def create_variable(self, bare_lang_data: dict) -> PyVariable:
        pass

    def create_value(self, bare_lang_data: dict) -> PyRvalue:
        pass

    def create_basic_value(self, bare_lang_data: dict) -> PyBasicValue:
        pass

    def create_collection(self, bare_lang_data: dict) -> PyCollection:
        pass

    def create_object(self, bare_lang_data: dict) -> PyObject:
        pass

    def create_class(self, bare_lang_data: dict) -> PyClass:
        pass

    def gps(self) -> None:
        pass


class PySnapshot(basic.Snapshot):
    def __init__(self, globals_data: 'python bld globals', locals_data: 'python bld locals', output: str):
        global_scene = PyScene(globals_data)
        local_scene = PyScene(locals_data)

        basic.Snapshot.__init__(self, OrderedDict([('globals', global_scene), ('locals', local_scene)]), output)
