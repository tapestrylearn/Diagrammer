# notes for meeting: talk about valuefactory and testing export vs object (i think we should test object for language and export for general scene)

from ..scene import basic
from collections import OrderedDict

import types

def is_instance_for_bld(bld: 'python bld value', type_obj: type) -> bool:
    # special cases
    # type is a special case because type() is its own function
    if bld['type_str'] == 'type':
        class A:
            pass

        return isinstance(A(), type)

    # general cases
    if bld['type_str'] == type_obj.__name__:
        return True

    try:
        return eval(f"isinstance({bld['type_str']}(), {type_obj.__name__})")
    except NameError:
        return False


def value_to_str(type_str: str, val: str) -> str:
    # todo: complex checks for custom value str representations
    return val


class BLDError:
    pass


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

    def construct(self, scene: 'PyScene', bld: dict):
        assert len(bld) == 1, f'PyVariable.construct: the length of bld {bld} is not 1'
        basic.BasicShape.construct(self, PyVariable.SIZE, PyVariable.SIZE, list(bld.keys())[0], '')
        val = scene.create_value(list(bld.values())[0])
        self._reference = PyReference(self, val)
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
    WHITELISTED_TYPES = {'int', 'str', 'bool', 'float', 'range', 'function', 'NoneType'}

    def __init__(self):
        basic.BasicShape.__init__(self)

    def construct(self, scene: 'PyScene', bld: dict):
        basic.BasicShape.construct(self, PyBasicValue.RADIUS * 2, PyBasicValue.RADIUS * 2, bld['type_str'], value_to_str(bld['type_str'], bld['val']))

    @staticmethod
    def is_basic_value(bld: 'python bld value'):
        return bld['type_str'] in PyBasicValue.WHITELISTED_TYPES


class PySimpleContents(basic.CollectionContents):
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
            raise ReorderException('PySimpleContents.reorder: attempting to reorder a nonreorderable objects')


class PySimpleCollection(basic.Collection, PyRvalue):
    ORDERED_COLLECTION_SETTINGS = basic.CollectionSettings(5, 5, 2, basic.CollectionSettings.HORIZONTAL, PyVariable.SIZE)
    UNORDERED_COLLECTION_SETTINGS = ORDERED_COLLECTION_SETTINGS

    def __init__(self):
        basic.Collection.__init__(self)

    def construct(self, scene: 'PyScene', bld: dict):
        if PySimpleCollection.is_ordered_collection(bld):
            settings = PySimpleCollection.ORDERED_COLLECTION_SETTINGS
            contents = PySimpleContents([scene.create_variable({f'{i}' : bld_val}) for i, bld_val in enumerate(bld['val'])], False)
        elif PySimpleCollection.is_unordered_collection(bld):
            settings = PySimpleCollection.UNORDERED_COLLECTION_SETTINGS

            if PySimpleCollection.is_mapping_collection(bld):
                contents = PySimpleContents([scene.create_variable({key : bld_val}) for key, bld_val in bld['val'].items()], True)
            else:
                contents = PySimpleContents([scene.create_variable({'' : bld_val}) for bld_val in bld['val']], True)
        else:
            raise TypeError(f'PySimpleCollection.construct: {bld} is neither an ordered collection nor an unordered collection')

        basic.Collection.construct(self, bld['type_str'], contents, settings)

    @staticmethod
    def is_simple_collection(bld: 'python bld value') -> bool:
        return not PyNamespaceCollection.is_namespace_collection(bld) and (PySimpleCollection.is_ordered_collection(bld) or PySimpleCollection.is_unordered_collection(bld))

    @staticmethod
    def is_ordered_collection(bld: 'python bld value') -> bool:
        valid_types = {list, tuple}
        return any(is_instance_for_bld(bld, collection_type) for collection_type in valid_types)

    @staticmethod
    def is_unordered_collection(bld: 'python bld value') -> bool:
        valid_types = {set, dict, types.MappingProxyType}
        return any(is_instance_for_bld(bld, collection_type) for collection_type in valid_types)

    @staticmethod
    def is_mapping_collection(bld: dict) -> bool:
        valid_types = {dict, types.MappingProxyType}
        return any(is_instance_for_bld(bld, collection_type) for collection_type in valid_types)

    @staticmethod
    def is_object_namespace_collection(bld: dict) -> bool:
        return bld['obj_type'] == 'obj'


class PyNamespaceContents(basic.CollectionContents):
    def __init__(self, sections: {str : [PyVariable]}, section_order: [str]):
        self._sections = sections
        self._section_order = section_order

    def __len__(self) -> int:
        return sum(len(section_contents) for section_contents in self._sections.items())

    def __iter__(self) -> 'iterator':
        def gen_contents():
            for section_name in self._section_order:
                for section in self._sections[section_name]:
                    yield section

        return gen_contents()

    def __getitem__(self, section_name: str) -> [PyVariable]:
        if type(section_name) == str:
            return self._sections[section_name]
        else:
            raise IndexError(f"Can't subscript object of type {type(self)} with index of type {type(section)}")

    def iter_by_section(self) -> 'iterator':
        def gen_sections():
            for section_name in self._section_order:
                yield sections[section_name]

        return gen_sections()

    def get_sections(self) -> {str : [PyVariable]}:
        return self._sections

    def get_section_order(self) -> [str]:
        return self._section_order

    def reorder_sections(self, i: int, j: int) -> None:
        self._section_order[i], self._section_order[j] = self._section_order[j], self._section_order[i]

    def reorder_within_section(self, section_name: str, i: int, j: int) -> None:
        self[section_name][i], self[section_name][j] = self[section_name][j], self[section_name][i]


class PyNamespaceCollection(basic.Collection):
    OBJECT = 0
    CLASS = 1
    COLLECTION_SETTINGS_DIR = {
        OBJECT : basic.CollectionSettings(5, 5, 5, basic.CollectionSettings.VERTICAL, PyVariable.SIZE),
        CLASS : basic.CollectionSettings(8, 8, 8, basic.CollectionSettings.VERTICAL, PyVariable.SIZE)
    }

    INTERNAL_VARS = {'__module__', '__dict__', '__weakref__', '__doc__'}

    def __init__(self, show_internal_vars: bool):
        basic.Collection.__init__(self)
        self._show_internal_vars = show_internal_vars

    def construct(self, scene: 'PyScene', bld: dict) -> None:
        if not PyNamespaceCollection.is_namespace_collection(bld):
            raise TypeError(f'PyNamespaceCollection.construct: {bld} is not an object collection')

        if PyNamespaceCollection.is_object_ddict(bld):
            sections = {'attrs' : [scene.create_variable({key : bld_val}) for key, bld_val in bld['val'].items()]}
            section_order = ['attrs']
            contents = PyNamespaceContents(sections, section_order)
            settings = PyNamespaceCollection.COLLECTION_SETTINGS_DIR[PyNamespaceCollection.OBJECT]
        elif PyNamespaceCollection.is_class_ddict(bld):
            section_order = ['internals', 'attrs', 'methods']
            sections = dict()

            for section_name in section_order:
                sections[section_name] = list()

            for name, bld_val in bld['val'].items():
                if not self._show_internal_vars and name in PyNamespaceCollection.INTERNAL_VARS:
                    continue

                if name in PyNamespaceCollection.INTERNAL_VARS:
                    section = 'internals'
                elif bld_val['type_str'] == 'function':
                    section = 'methods'
                else:
                    section = 'attrs'

                var = scene.create_variable({name : bld_val})
                sections[section].append(var)

            contents = PyNamespaceContents(sections, section_order)
            settings = PyNamespaceCollection.COLLECTION_SETTINGS_DIR[PyNamespaceCollection.CLASS]
        else:
            raise TypeError(f'PyNamespaceCollection.construct: {bld} is a namespace collection but neither an object nor a class ddict')

        basic.Collection.construct(self, bld['type_str'], contents, settings)

    @staticmethod
    def is_namespace_collection(bld: dict) -> bool:
        return 'obj_type' in bld

    @staticmethod
    def is_object_ddict(bld: dict) -> bool:
        # the reason is_namespace_collection() is checked here is because when you're calling this function on a non-object ddict you can't have it crash
        return PyNamespaceCollection.is_namespace_collection(bld) and bld['obj_type'] == 'obj'

    @staticmethod
    def is_class_ddict(bld: dict) -> bool:
        # the reason is_namespace_collection() is checked here is because when you're calling this function on a non-object ddict you can't have it crash
        return PyNamespaceCollection.is_namespace_collection(bld) and bld['obj_type'] == 'class'


class PyNamespace(basic.Container, PyRvalue):
    OBJECT = 0
    CLASS = 1
    MARGINS = {
        OBJECT: (3, 3),
        CLASS: (5, 5)
    }

    def __init__(self):
        basic.Container.__init__(self)

    def construct(self, scene: 'PyScene', bld: dict):
        coll = scene.create_value(bld['val'])

        if PyNamespace.is_object(bld):
            margins = PyNamespace.MARGINS[PyNamespace.OBJECT]
        elif PyNamespace.is_class(bld):
            margins = PyNamespace.MARGINS[PyNamespace.CLASS]
        else:
            raise TypeError(f'PyContainer.construct: {bld} is neither an object nor a class')

        basic.Container.construct(self, bld['type_str'], coll, margins[0], margins[1])

    @staticmethod
    def is_namespace(bld: 'python bld value'):
        return PyNamespace.is_object(bld) or PyNamespace.is_class(bld)

    @staticmethod
    def is_object(bld: 'python bld value'):
        return PyNamespaceCollection.is_object_ddict(bld['val'])

    @staticmethod
    def is_class(bld: 'python bld value'):
        return PyNamespaceCollection.is_class_ddict(bld['val'])


class PySceneSettings:
    def __init__(self, show_class_internal_vars = False):
        self.show_class_internal_vars = show_class_internal_vars


class PyScene(basic.Scene):
    def __init__(self, scene_settings: PySceneSettings):
        basic.Scene.__init__(self)

        self._scene_settings = scene_settings
        self._nonvalue_id = -1

    def construct(self, bld: dict):
        for var_name, value_data in bld.items():
            self.create_variable({var : value_data})

    # NOTE: add_ functions return None, create_ functions return what they create
    def add_reference(self, ref: PyReference) -> None:
        self._add_nonvalue_obj(ref)

    def create_variable(self, bld: dict) -> PyVariable:
        variable = PyVariable()
        variable.construct(self, bld)
        self._add_nonvalue_obj(variable)

        return variable

    def create_value(self, bld: dict) -> PyRvalue:
        if bld['id'] in self._directory:
            return self._directory[bld['id']]
        else:
            if PyBasicValue.is_basic_value(bld):
                val = PyBasicValue()
            elif PySimpleCollection.is_simple_collection(bld):
                val = PySimpleCollection()
            elif PyNamespace.is_namespace(bld):
                val = PyNamespace()
            elif PyNamespaceCollection.is_namespace_collection(bld):
                val = PyNamespaceCollection(self._scene_settings.show_class_internal_vars)
            else:
                raise TypeError(f'PyScene.create_value: {bld} is not a valid value bld')

            self._directory[bld['id']] = val
            val.construct(self, bld)

            return val

    def _add_nonvalue_obj(self, obj: 'non-value object') -> None:
        self._directory[self._nonvalue_id] = obj
        self._nonvalue_id -= 1

    def gps(self) -> None:
        for obj in self._directory.values():
            obj.set_pos(random.random() * 500, random.random() * 500)

    def debug_get_settings(self) -> PySceneSettings:
        return self._scene_settings


class PySnapshot(basic.Snapshot):
    def __init__(self, globals_data: 'python bld globals', locals_data: 'python bld locals', output: str):
        global_scene = PyScene()
        global_scene.construct(globals_data)

        local_scene = PyScene()
        local_scene.construct(locals_data)

        basic.Snapshot.__init__(self, OrderedDict([('globals', global_scene), ('locals', local_scene)]), output)
