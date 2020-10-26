# notes for meeting: talk about valuefactory and testing export vs object (i think we should test object for language and export for general scene)

from ..scene import basic
from collections import OrderedDict, defaultdict

import types
import random
import json
import time


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

    if type_str == 'range':
        args = val.split('(')[1][:-1].split(',') # basically take only stuff between parens and divide into args
        return ':'.join(arg.strip() for arg in args)
    elif type_str in {'int', 'str', 'bool', 'float', 'NoneType'}:
        return val
    else:
        return '...'


class BLDError(Exception):
    pass


class PyConstruct:
    def is_constructed(self) -> bool:
        pass


class PyRvalue(PyConstruct):
    pass


class PyVariable(basic.Square, PyConstruct):
    SIZE = 50

    # the reason PyVariable doesn't have a construct is because it doesn't have a bld, and construct takes in a bld
    def __init__(self, name: str):
        basic.Square.__init__(self)
        basic.Square.construct(self, PyVariable.SIZE, name, '')

    def set_ref(self, reference: 'PyReference') -> None:
        self._reference = reference

    def get_head_obj(self) -> PyRvalue:
        return self._reference.get_head_obj()


class PyReference(basic.Arrow, PyConstruct):
    SETTINGS = basic.ArrowSettings(
        basic.ArrowSettings.SOLID,
        basic.ArrowSettings.EDGE,
        basic.ArrowSettings.CENTER
    )

    def __init__(self, tail_obj: PyVariable, head_obj: PyRvalue):
        basic.Arrow.__init__(self, tail_obj, head_obj, PyReference.SETTINGS)

    def get_head_obj(self) -> float:
        return self._head_obj


class PyBasicValue(basic.RoundedRect, PyRvalue):
    RADIUS = 25
    TEXT_MARGIN = 10
    LETTER_WIDTH = 8
    WHITELISTED_TYPES = {'int', 'str', 'bool', 'float', 'range', 'function', 'NoneType', 'getset_descriptor', types.FunctionType.__name__, types.BuiltinFunctionType.__name__, types.MethodDescriptorType.__name__,
        types.WrapperDescriptorType.__name__, types.MethodWrapperType.__name__, types.ClassMethodDescriptorType.__name__}

    def construct(self, scene: 'PyScene', bld: dict):
        text_width = len(bld['val']) * PyBasicValue.LETTER_WIDTH # + 2 for the quotes
        width = max(PyBasicValue.TEXT_MARGIN * 2 + text_width, PyBasicValue.RADIUS * 2)
        basic.RoundedRect.construct(self, width, PyBasicValue.RADIUS * 2, PyBasicValue.RADIUS, bld['type_str'], value_to_str(bld['type_str'], bld['val']))

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

    def __getitem__(self, index: int) -> PyVariable:
        if type(index) == int:
            return self._elements[index]
        else:
            raise IndexError(f"Can't subscript object of type {type(self)} with index of type {type(index)}")

    def reorder(self, i: int, j: int):
        if self._reorderable:
            self._elements[i], self._elements[j] = self._elements[j], self._elements[i]
        else:
            raise ReorderException('PySimpleContents.reorder: attempting to reorder a nonreorderable objects')


class PySimpleCollection(basic.Collection, PyRvalue):
    SETTINGS = basic.CollectionSettings(15, 15, 50, basic.CollectionSettings.HORIZONTAL, PyVariable.SIZE, 20)

    def construct(self, scene: 'PyScene', bld: dict):
        if PySimpleCollection.is_ordered_collection(bld):
            contents = PySimpleContents([scene.create_variable(f'{i}', bld_val) for i, bld_val in enumerate(bld['val'])], False)
        elif PySimpleCollection.is_unordered_collection(bld):
            if PySimpleCollection.is_mapping_collection(bld):
                contents = PySimpleContents([scene.create_variable(key, bld_val) for key, bld_val in bld['val'].items()], True)
            else:
                contents = PySimpleContents([scene.create_variable('', bld_val) for bld_val in bld['val']], True)
        else:
            raise BLDError(f'PySimpleCollection.construct: {bld} is neither an ordered collection nor an unordered collection')

        basic.Collection.construct(self, bld['type_str'], contents, PySimpleCollection.SETTINGS)

    @staticmethod
    def is_simple_collection(bld: 'python bld value') -> bool:
        return PySimpleCollection.is_ordered_collection(bld) or PySimpleCollection.is_unordered_collection(bld)

    @staticmethod
    def is_ordered_collection(bld: 'python bld value') -> bool:
        valid_types = {list, tuple}
        return not PyNamespaceCollection.is_namespace_collection(bld) and any(is_instance_for_bld(bld, collection_type) for collection_type in valid_types)

    @staticmethod
    def is_unordered_collection(bld: 'python bld value') -> bool:
        valid_types = {set, dict, types.MappingProxyType}
        return not PyNamespaceCollection.is_namespace_collection(bld) and any(is_instance_for_bld(bld, collection_type) for collection_type in valid_types)

    @staticmethod
    def is_mapping_collection(bld: dict) -> bool:
        valid_types = {dict, types.MappingProxyType}
        return not PyNamespaceCollection.is_namespace_collection(bld) and any(is_instance_for_bld(bld, collection_type) for collection_type in valid_types)


class PyNamespaceContents(basic.CollectionContents):
    def __init__(self, sections: {str : [PyVariable]}, section_order: [str]):
        self._sections = sections
        self._section_order = section_order

    def __len__(self) -> int:
        return sum(len(section_contents) for section_contents in self._sections.values())

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
            raise IndexError(f"Can't subscript object of type {type(self)} with index of type {type(section_name)}")

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


class PyNamespaceCollection(basic.Collection, PyRvalue):
    OBJECT = 0
    CLASS = 1
    COLLECTION_SETTINGS_DIR = {
        OBJECT : basic.CollectionSettings(10, 10, 50, basic.CollectionSettings.HORIZONTAL, PyVariable.SIZE, 18),
        CLASS : basic.CollectionSettings(10, 10, 50, basic.CollectionSettings.HORIZONTAL, PyVariable.SIZE, 15)
    }

    INTERNAL_VARS = {'__module__', '__dict__', '__weakref__', '__doc__'}

    def construct(self, scene: 'PyScene', bld: dict, **settings) -> None:
        if not PyNamespaceCollection.is_namespace_collection(bld):
            raise BLDError(f'PyNamespaceCollection.construct: {bld} is not an object collection')

        if PyNamespaceCollection.is_object_ddict(bld):
            sections = {'attrs' : [scene.create_variable(key, bld_val) for key, bld_val in bld['val'].items()]}
            section_order = ['attrs']

            contents = PyNamespaceContents(sections, section_order)
            collection_settings = PyNamespaceCollection.COLLECTION_SETTINGS_DIR[PyNamespaceCollection.OBJECT]
        elif PyNamespaceCollection.is_class_ddict(bld):
            section_order = ['internals', 'attrs', 'methods']
            sections = {section : [] for section in section_order}

            for name, bld_val in bld['val'].items():
                if not settings['show_class_internal_vars'] and name in PyNamespaceCollection.INTERNAL_VARS:
                    continue

                if name in PyNamespaceCollection.INTERNAL_VARS:
                    section = 'internals'
                elif bld_val['type_str'] == 'function': # this doesn't always work i think (see list of "function-like" types)
                    section = 'methods'
                else:
                    section = 'attrs'

                var = scene.create_variable(name, bld_val)
                sections[section].append(var)

            contents = PyNamespaceContents(sections, section_order)
            collection_settings = PyNamespaceCollection.COLLECTION_SETTINGS_DIR[PyNamespaceCollection.CLASS]
        else:
            raise BLDError(f'PyNamespaceCollection.construct: {bld} is a namespace collection but neither an object nor a class ddict')

        basic.Collection.construct(self, bld['type_str'], contents, collection_settings)

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
        OBJECT: (8, 8),
        CLASS: (12, 12)
    }
    CORNER_RADIUS = 20

    def construct(self, scene: 'PyScene', bld: dict):
        coll = scene.create_value(bld['val'])

        if PyNamespace.is_object(bld):
            margins = PyNamespace.MARGINS[PyNamespace.OBJECT]
        elif PyNamespace.is_class(bld):
            margins = PyNamespace.MARGINS[PyNamespace.CLASS]
        else:
            raise BLDError(f'PyContainer.construct: {bld} is neither an object nor a class')

        basic.Container.construct(self, bld['type_str'], coll, margins[0], margins[1], PyNamespace.CORNER_RADIUS)

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

    @staticmethod
    def from_dict(settings_dict: {str : object}) -> 'PySceneSettings':
        show_class_internal_vars = settings_dict['show_internal_class_vars'] if 'show_internal_class_vars' in settings_dict else None

        return PySceneSettings(show_class_internal_vars=show_class_internal_vars)


class PyScene(basic.Scene):
    GRID_SIZE = 100
    MIN_GRID_MARGIN = 5

    def __init__(self, scene_settings: PySceneSettings):
        basic.Scene.__init__(self)

        self._scene_settings = scene_settings
        self._nonvalue_id = -1

    def construct(self, bld: dict):
        for var_name, value_bld in bld.items():
            self.create_variable(var_name, value_bld)

        non_positionable_objects = set()

        for obj in self._directory.values():
            if type(obj) == PySimpleCollection or type(obj) == PyNamespaceCollection:
                for var in obj:
                    non_positionable_objects.add(var)
            elif type(obj) == PyNamespace:
                non_positionable_objects.add(obj.get_coll())

        # cache useful groups
        self._positionable_objects = [obj for obj in self._directory.values() if type(obj) != PyReference and obj not in non_positionable_objects]
        self._positionable_rvalues = [obj for obj in self._positionable_objects if type(obj) != PyVariable] # collections inside namespaces aren't positionable
        self._references = [obj for obj in self._directory.values() if type(obj) == PyReference]
        self._variables = [obj for obj in self._directory.values() if type(obj) == PyVariable]
        self._edge_variables = [obj for obj in self._positionable_objects if type(obj) == PyVariable]
        self._edge_simple_collections = [var.get_head_obj() for var in self._edge_variables if type(var.get_head_obj()) == PySimpleCollection]
        self._battery_variables = [var for var in self._edge_variables if type(var.get_head_obj()) == PyBasicValue and var.get_head_obj().get_in_degree() == 1]

    # NOTE: add_ functions return None, create_ functions return what they create
    def create_variable(self, name: str, bld: dict) -> PyVariable:
        val = self.create_value(bld)
        var = PyVariable(name)
        ref = PyReference(var, val)
        var.set_ref(ref)

        self._add_nonvalue_obj(ref)
        self._add_nonvalue_obj(var)

        if type(val) is PyBasicValue:
            val.inc_in_degree()

        return var

    def create_value(self, bld: dict) -> PyRvalue:
        if bld['id'] in self._directory:
            return self._directory[bld['id']]
        else:
            settings = {}

            if PyBasicValue.is_basic_value(bld):
                val = PyBasicValue()
            elif PySimpleCollection.is_simple_collection(bld):
                val = PySimpleCollection()
            elif PyNamespace.is_namespace(bld):
                val = PyNamespace()
            elif PyNamespaceCollection.is_namespace_collection(bld):
                val = PyNamespaceCollection()

                settings['show_class_internal_vars'] = self._scene_settings.show_class_internal_vars
            else:
                raise BLDError(f'PyScene.create_value: {bld} is not a valid value bld')

            self._directory[bld['id']] = val
            val.construct(self, bld, **settings)

            return val

    def get_directory(self) -> {int : PyRvalue}:
        return self._directory

    def _add_nonvalue_obj(self, obj: 'non-value object') -> None:
        self._directory[self._nonvalue_id] = obj
        self._nonvalue_id -= 1

    def set_grid(self, obj: PyConstruct, r: int, c: int):
        grid_margin = (PyScene.GRID_SIZE - obj.get_height()) / 2
        obj.set_corner_pos(grid_margin + c * PyScene.GRID_SIZE, grid_margin + r * PyScene.GRID_SIZE)

    def gps(self) -> None:
        current_row = 0

        for var in self._battery_variables:
            self.set_grid(var, current_row, 0)
            self.set_grid(var.get_head_obj(), current_row, 1)
            current_row += 1

        for var in self._edge_variables:
            if var in self._battery_variables:
                continue

            self.set_grid(var, current_row, 0)

            val = var.get_head_obj()

            if not val.is_positioned():
                if type(val) is PyBasicValue:
                    self.set_grid(val, current_row, 1)
                elif type(val) in {PySimpleCollection, PyNamespace}:
                    current_row = self._position_collection(val, current_row, 1)

            current_row += 1

        for obj in self._positionable_objects:
            if not obj.is_positioned():
                self.set_grid(obj, 10, 10)

        if len(self._positionable_objects) > 0:
            self._width = max(obj.get_x() + obj.get_width() for obj in self._positionable_objects)
            self._height = max(obj.get_y() + obj.get_height() for obj in self._positionable_objects)
        else:
            self._width = self._height = 0

    def _position_collection(self, collection_or_container: 'basic.Collection or basic.Container', start_row: int, start_col: int) -> None:
        current_row = start_row
        self.set_grid(collection_or_container, current_row, start_col)
        collection = collection_or_container if type(collection_or_container) is PySimpleCollection else collection_or_container.get_coll()

        # position 1 wide basic values
        one_wides_exist = False

        for (i, var) in enumerate(collection):
            one_wides_exist = True
            val = var.get_head_obj()

            if type(val) == PyBasicValue and val.get_width() < PyScene.GRID_SIZE - PyScene.MIN_GRID_MARGIN * 2:
                if not val.is_positioned():
                    self.set_grid(val, current_row, start_col + i)

        if one_wides_exist:
            current_row = current_row + 1

        # position >1 wide basic values
        for (i, var) in reversed([(inner_i, inner_var) for (inner_i, inner_var) in enumerate(collection)]):
            val = var.get_head_obj()

            if type(val) == PyBasicValue and val.get_width() > PyScene.GRID_SIZE - PyScene.MIN_GRID_MARGIN * 2:
                if not val.is_positioned():
                    current_row += 1
                    self.set_grid(val, current_row, start_col + i)

        # position next layer of collections
        next_layer_current_row = start_row + 1
        next_layer_start_col = start_col + len(collection) + 1

        for i, val in enumerate([var.get_head_obj() for var in collection if type(var.get_head_obj()) in {PySimpleCollection, PyNamespace}]):
            if (i != 0):
                next_layer_current_row += 1

            if not val.is_positioned():
                next_layer_current_row = self._position_collection(val, next_layer_current_row, next_layer_start_col)

        return max(current_row, next_layer_current_row)


class PySnapshot(basic.Snapshot):
    def __init__(self, globals_bld: 'python bld globals', locals_bld: 'python bld locals', output: str, error: bool, scene_settings: PySceneSettings):
        print(json.dumps(globals_bld, indent=2))

        global_scene = PyScene(scene_settings)
        global_scene.construct(globals_bld)
        global_scene.gps()

        local_scene = PyScene(scene_settings)
        local_scene.construct(locals_bld)
        local_scene.gps()

        basic.Snapshot.__init__(self, {'globals' : global_scene, 'locals' : local_scene}, output, error)
