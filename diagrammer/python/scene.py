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

    def __init__(self):
        basic.BasicShape.__init__(self)

    def construct(self, scene: 'PyScene', name: str, head_obj_bld: dict):
        basic.BasicShape.construct(self, PyVariable.SIZE, PyVariable.SIZE, name, '')
        head_obj = scene.create_value(head_obj_bld)
        self._reference = PyReference(self, head_obj)
        scene.add_reference(self._reference)

    def get_head_obj(self) -> PyRvalue:
        return self._reference.get_head_obj()


class PyReference(basic.Arrow, PyConstruct):
    OPTIONS = basic.ArrowOptions(
        basic.ArrowOptions.SOLID,
        basic.ArrowOptions.EDGE,
        basic.ArrowOptions.CENTER
    )

    def __init__(self, tail_obj: PyVariable, head_obj: PyRvalue):
        basic.Arrow.__init__(self, tail_obj, head_obj, PyReference.OPTIONS)

    def get_head_obj(self) -> float:
        return self._head_obj


class PyBasicValue(basic.BasicShape, PyRvalue):
    RADIUS = 25
    SHAPE = basic.Shape.CIRCLE

    def __init__(self):
        basic.BasicShape.__init__(self)

    def construct(self, scene: 'PyScene', bld: dict):
        basic.BasicShape.construct(self, PyBasicValue.RADIUS * 2, PyBasicValue.RADIUS * 2, bld['type_str'], value_to_str(bld['type_str'], bld['val']))

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
            contents = PyCollectionContents([scene.create_variable(f'{i}', bld_val) for i, bld_val in enumerate(bld['val'])], False)
        elif PyCollection.is_unordered_collection(bld):
            settings = PyCollection.UNORDERED_COLLECTION_SETTINGS

            if PyCollection.is_mapping_collection(bld):
                contents = PyCollectionContents([scene.create_variable(key, bld_val) for key, bld_val in bld['val'].items()], True)
            else:
                contents = PyCollectionContents([scene.create_variable('', bld_val) for bld_val in bld['val']], True)
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

    # def reorder(self, i: int, j: int):
    #     self._sections[i], self._sections[j] = self._sections[j], self._sections[i]

    def reorder_within_section(self, section: str, i: int, j: int):
        self[section][i], self[section][j] = self[section][j], self[section][i]


class PyObject(basic.Container, PyRvalue):
    COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 3, basic.CollectionSettings.VERTICAL, PyVariable.SIZE)
    SECTION_ORDER = ['attrs']

    def __init__(self):
        basic.Container.__init__(self)

    def construct(self, scene: 'PyScene', bld: dict):
        contents = []

        for variable_name, value_data in bld['val'].items():
            variable = scene.create_varlabe({variable_name : value_data})
            contents.append(variable)

        attrs = self._init_attrs(contents)

        self.set_header(bld['type_str'])
        self.set_attrs(attrs)

    def _init_attrs(self, contents: [PyVariable], **settings) -> basic.Collection:
        return PyObjectContents([
            ('attrs', contents)
        ])

    @staticmethod
    def is_object(bld: 'python bld value'):
        return type(bld['val']) == dict and bld['val'].keys() == {'id', 'type_str', 'val'} and not PyClass.is_class(bld)


class PyClass(PyObject):
    COLLECTION_SETTINGS = basic.CollectionSettings(8, 8, 5, basic.CollectionSettings.VERTICAL, PyVariable.SIZE)
    INTERNAL_VARS = {'__module__', '__dict__', '__weakref__', '__doc__'}

    def __init__(self):
        PyObject.__init__(self)

    def _init_attrs(self, contents: [PyVariable], show_internal_vars: bool) -> basic.Collection:
        if not show_internal_vars:
            section_order = ['attrs', 'methods']
        else:
            section_order = ['internal', 'attrs', 'methods']

        sections = {}

        for section in section_order:
            sections[section] = []

        for name, bld_val in bld_class['val'].items():
            if not show_internal_vars and name in PyClass.INTERNAL_VARS:
                continue

            if name in PyClass.INTERNAL_VARS:
                section = 'internal'
            elif bld_val['type_str'] == 'function':
                section = 'methods'
            else:
                section = 'attrs'

            var = PyVariable(name, bld_val)
            sections[section].append([var])

        return PyObjectContents({section : sections[section] for section in section_order})

    def construct(self, scene: 'PyScene', bld: dict):
        contents = []

        for variable_name, value_data in bld['val'].items():
            variable = scene.create_varlabe({variable_name : value_data})
            contents.append(variable)

        attrs = self._init_attrs(contents, False)

        self.set_header(bld['type_str'])
        self.set_attrs(attrs)

    @staticmethod
    def is_class(bld: 'python bld value'):
        return bld['type_str'] == 'type'


class PyScene(basic.Scene):
    def __init__(self): # TODO: add settings
        basic.Scene.__init__(self)

        self._nonvalue_id = -1

    def construct(self, bld: dict):
        for var_name, value_data in bld.items():
            self.create_variable({var : value_data})

    # NOTE: add_ functions return None, create_ functions return what they create
    def add_reference(self, ref: PyReference) -> None:
        self._add_nonvalue_obj(ref)

    def create_variable(self, name: str, head_obj_bld: dict) -> PyVariable:
        variable = PyVariable()
        variable.construct(self, name, head_obj_bld)
        self._add_nonvalue_obj(variable)

        return variable

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
        global_scene = PyScene()
        global_scene.construct(globals_data)

        local_scene = PyScene()
        local_scene.construct(locals_data)

        basic.Snapshot.__init__(self, OrderedDict([('globals', global_scene), ('locals', local_scene)]), output)
