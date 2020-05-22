# notes for meeting: talk about valuefactory and testing export vs object (i think we should test object for language and export for general scene)

from ..scene import basic
from collections import OrderedDict

import types

def is_type(bld: 'python bld value', type_obj: type) -> bool:
    if bld['type_str'] == type_obj.__name__:
        return True

    try:
        return eval(f"isinstance({bld['type_str']}(), {type_obj.__name__})")
    except NameError:
        return False


def value_to_str(type_str: str, val: str) -> str:
    # todo: complex checks for custom value str representations
    return val


class PyConstruct:
    def is_constructed(self) -> bool:
        pass


class PyRvalue(PyConstruct):
    pass


class PyVariable(basic.BasicShape, PyConstruct):
    SIZE = 50
    SHAPE = basic.Shape.SQUARE

    def __init__(self, name: str):
        basic.BasicShape.__init__(self, PyVariable.SIZE, PyVariable.SIZE, name, '')

    def construct(self, scene: 'PyScene', bld: dict):
        val = scene.create_value(bld)
        scene.add_arrow(PyReference(val, self))


class PyReference(basic.Arrow):
    OPTIONS = basic.ArrowOptions(
        basic.ArrowOptions.SOLID,
        basic.ArrowOptions.EDGE,
        basic.ArrowOptions.CENTER
    )

    def __init__(self, head_obj: PyRvalue, tail_obj: PyVariable):
        basic.Arrow.__init__(self, head_obj, tail_obj, PyReference.OPTIONS)


class PyBasicValue(basic.BasicShape, PyRvalue):
    RADIUS = 25
    SHAPE = basic.Shape.CIRCLE

    def __init__(self):
        basic.BasicShape.__init__(self, width = PyBasicValue.RADIUS * 2, height = PyBasicValue.RADIUS * 2)

    def construct(self, scene: 'PyScene', bld: dict):
        self.set_header(bld['type_str'])
        self.set_content(value_to_str(bld['type_str'], bld['val']))

    @staticmethod
    def is_basic_value(bld: 'python bld value'):
        return not (PyCollection.is_collection(bld) or PyObject.is_object(bld) or PyClass.is_class(bld))


class PyCollectionContents(basic.CollectionContents):
    def __init__(self, elements: [PyVariable], reorderable: bool):
        self._elements = elements
        self._reorderable = reorderable

    def __len__(self) -> int:
        return len(self._elements)

    def __iter__(self) -> 'iterator':
        return iter(self._elements)

    def reorder(self, i: int, j: int):
        if self._reorderable:
            self._elements[i], self._elements[j] = self._elements[j], self._elements[i]
        else:
            raise ReorderException('PyCollectionContents.reorder: attempting to reorder a nonreorderable objects')


class PyCollection(basic.Collection, PyRvalue):
    ORDERED_COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 0, basic.CollectionSettings.HORIZONTAL, PyVariable.SIZE)
    UNORDERED_COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 2, basic.CollectionSettings.HORIZONTAL, PyVariable.SIZE)

    def __init__(self):
        basic.Collection.__init__(self)

    def construct(self, scene: 'PyScene', bld: dict):
        if PyCollection.is_ordered_collection(bld):
            settings = PyCollection.ORDERED_COLLECTION_SETTINGS
            contents = PyCollectionContents([scene.create_variable(f'{i}', bld) for i, bld in enumerate(bld['val'])], True)
        elif PyCollection.is_unordered_collection(bld):
            settings = PyCollection.UNORDERED_COLLECTION_SETTINGS

            if PyCollection.is_mapping_collection(bld):
                contents = PyCollectionContents([scene.create_variable(key, bld) for key, bld in bld['val'].items()], False)
            else:
                contents = PyCollectionContents([scene.create_variable('', bld) for bld in bld['val']], False)
        else:
            raise TypeError(f'PyCollection.construct: {bld} is neither an ordered collection nor an unordered collection')

        basic.Collection.construct(self, bld['type_str'], contents, settings)

    @staticmethod
    def is_collection(bld: 'python bld value') -> bool:
        return PyCollection.is_ordered_collection(bld) or PyCollection.is_unordered_collection(bld)

    @staticmethod
    def is_ordered_collection(bld: 'python bld value') -> bool:
        valid_types = {list, tuple}
        return any(is_type(bld, collection_type) for collection_type in valid_types)

    @staticmethod
    def is_unordered_collection(bld: 'python bld value') -> bool:
        valid_types = {set, dict, types.MappingProxyType}
        return any(is_type(bld, collection_type) for collection_type in valid_types)

    @staticmethod
    def is_mapping_collection(bld: dict) -> bool:
        valid_types = {dict, types.MappingProxyType}
        return any(is_type(bld, collection_type) for collection_type in valid_types)


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
    COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 3, basic.CollectionSettings.VERTICAL, PyVariable.SIZE)
    SECTION_ORDER = ['attrs']

    def __init__(self, type_str: str = None, contents: [PyVariable] = None):
        pass

    def construct(self, scene: 'PyScene', bld: dict):
        pass

    @staticmethod
    def is_object(bld: 'python bld value'):
        return type(bld['val']) == dict and bld['val'].keys() == {'id', 'type_str', 'val'} and not PyClass.is_class(bld)


class PyClass(basic.Container, PyRvalue):
    COLLECTION_SETTINGS = basic.CollectionSettings(8, 8, 5, basic.CollectionSettings.VERTICAL, PyVariable.SIZE)
    INTERNAL_VARS = {'__module__', '__dict__', '__weakref__', '__doc__'}

    def __init__(self, obj_id: int, bld: 'python bld class', show_class_hidden_vars = False):
        # if not PyClass.is_class(bld):
        #     raise TypeError(f'PyClass.__init__: {bld} is not a python bld class')

        # PyRvalue.__init__(self, obj_id)

        # if not show_class_hidden_vars:
        #     section_order = ['attrs', 'methods']
        # else:
        #     section_order = ['hidden', 'attrs', 'methods']

        # sections = dict()

        # for section in section_order:
        #     sections[section] = list()

        # for name, bld in bld['val']['val'].items():
        #     if not show_class_hidden_vars and name in PyClass.HIDDEN_VARS:
        #         continue

        #     if name in PyClass.HIDDEN_VARS:
        #         section = 'hidden'
        #     elif bld['type_str'] == 'function':
        #         section = 'methods'
        #     else:
        #         section = 'attrs'

        #     var = PyVariable(name, bld)
        #     sections[section].append([var])

        # col = basic.ComplexCollection(PyClass.COL_SET, bld['val']['type_str'], sections, section_order, PyClass.SECTION_REORDERABLE)

        # basic.Container.__init__(self, bld['type_str'], col)
        pass

    def construct(self, scene: 'PyScene', bld: dict):
        pass

    @staticmethod
    def is_class(bld: 'python bld value'):
        return bld['type_str'] == 'type'


class PyScene(basic.Scene):
    def __init__(self): # TODO: add settings
        # basic.Scene.__init__(self)
        # create scene contents
        self._directory = dict()
        self._nonvalue_id = -1

    def construct(self, bld: 'python bld scene'):
        pass

    # NOTE: add_ functions return None, create_ functions return what they create
    def add_arrow(self, arrow: PyReference) -> None:
        self._add_nonvalue_obj(arrow)

    def create_variable(self, name: str, bld: dict) -> PyVariable:
        var = PyVariable(name)
        self._add_nonvalue_obj(var)
        var.construct(self, bld)
        return var

    def create_value(self, bld: dict) -> PyRvalue:
        if PyBasicValue.is_basic_value(bld):
            val = PyBasicValue()
        elif PyCollection.is_collection(bld):
            val = PyCollection()
        elif PyObject.is_object(bld):
            val = PyObject()
        elif PyClass.is_class(bld):
            val = PyClass()
        else:
            raise TypeError(f'PyScene.create_value: {bld} is not a valid value bld')

        self._add_value_obj(bld['id'], val)
        val.construct(self, bld)
        return val

    def _add_nonvalue_obj(self, obj: 'non-value object') -> None:
        self._directory[self._nonvalue_id] = obj
        self._nonvalue_id -= 1

    def _add_value_obj(self, id: int, obj: PyRvalue) -> None:
        self._directory[id] = obj

    def gps(self) -> None:
        for obj in self._directory.values():
            obj.set_pos(random.random() * 500, random.random() * 500)


class PySnapshot(basic.Snapshot):
    def __init__(self, globals_data: 'python bld globals', locals_data: 'python bld locals', output: str):
        global_scene = PyScene(globals_data)
        local_scene = PyScene(locals_data)

        basic.Snapshot.__init__(self, OrderedDict([('globals', global_scene), ('locals', local_scene)]), output)
