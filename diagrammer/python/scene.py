# notes for meeting: talk about valuefactory and testing export vs object (i think we should test object for language and export for general scene)

from ..scene import basic
from collections import OrderedDict


# is_type solution:
#   - return type_str == str(type) OR
#   - type check:
#       - first test value directly: isinstance(bld_val['val'], type_obj.__name__)
#       - if value test fails, try no args init (like current)
#       - if no args init fails, either return false or throw exception (not sure which)
#       - another option: use regex to detect "special obj" syntax -- e.g. <zip object at ...>
#           - somehow transform special obj into usable obj
#           - r'<.+ at [a-z0-9]+>'
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

# is_blank methods
def is_primitive(bld_val: 'python bld value'):
    return not (is_collection(bld_val) or is_object(bld_val) or is_class(bld_val))

def is_collection(bld_val: 'python bld value') -> bool:
    return is_ordered_collection(bld_val) or is_unordered_collection(bld_val)

def is_ordered_collection(bld_val: 'python bld value') -> bool:
    return is_type(bld_val, list) or is_type(bld_val, tuple)

def is_unordered_collection(bld_val: 'python bld value') -> bool:
    return is_type(bld_val, set) or is_type(bld_val, dict)

def is_object(bld_val: 'python bld value'):
    return type(bld_val['val']) == dict and bld_val['val'].keys() == {'id', 'type_str', 'val'} and not PyClass.is_class(bld_val)

def is_class(bld_val: 'python bld value'):
    return bld_val['type_str'] == 'type'


class PyPrimitive(basic.BasicShape):
    RADIUS = 25
    SHAPE = basic.CIRCLE

    def __init__(self, type_str: str, value_str: str):
        if not PyPrimitive.is_primitive(bld_prim):
            raise TypeError(f'PyPrimitive.__init__: {bld_prim} is not a python bld primitive')

        basic.BasicShape.__init__(self, PyPrimitive.RADIUS * 2, PyPrimitive.RADIUS * 2, bld_prim['type_str'], value_to_str(bld_prim['type_str'], bld_prim['val']), PyPrimitive.SHAPE)


class PyVariable(basic.BasicShape):
    SIZE = 50
    SHAPE = basic.SQUARE

    def __init__(self, name: str, bld_val: 'python bld value'):
        basic.BasicShape.__init__(self, PyVariable.SIZE, PyVariable.SIZE, name, '', PyVariable.SHAPE)
        self._head_obj = scene_creator.create_value(bld_val)


class PyCollection(basic.SimpleCollection):
    ORDERED_COL_SET = basic.CollectionSettings(5, 5, 0, basic.CollectionSettings.HORIZONTAL)
    UNORDERED_COL_SET = basic.CollectionSettings(5, 5, 2, basic.CollectionSettings.HORIZONTAL)

    def __init__(self, bld_col: 'python bld collection'):
        if not PyCollection.is_collection(bld_col):
            raise TypeError(f'PyCollection.__init__: {bld_col} is not a python bld collection')

        if PyCollection.is_ordered_collection(bld_col):
            reorderable = False
        else:
            reorderable = True

        vars = list()

        if PyCollection.is_ordered_collection(bld_col):
            col_set = PyCollection.ORDERED_COL_SET

            for (i, bld_val) in enumerate(bld_col['val']):
                var = PyVariable(str(i), bld_val)
                vars.append(var)
        elif PyCollection.is_unordered_collection(bld_col):
            col_set = PyCollection.UNORDERED_COL_SET

            if is_type(bld_col, set):
                for bld_val in bld_col['val']:
                    var = PyVariable('', bld_val)
                    vars.append(var)
            elif is_type(bld_col, dict):
                for name, bld_val in bld_col['val'].items():
                    var = PyVariable(name, bld_val)
                    vars.append(var)

        basic.SimpleCollection.__init__(self, col_set, bld_col['type_str'], vars, reorderable)


class PyObject(basic.Container):
    COL_SET = basic.CollectionSettings(5, 5, 3, basic.CollectionSettings.VERTICAL)
    SECTION_REORDERABLE = False
    SECTION_ORDER = ['attrs']

    def __init__(self, bld_obj: 'python bld object'):
        if not PyObject.is_object(bld_obj):
            raise TypeError(f'PyObject.__init__: {bld_obj} is not a python bld object')

        sections = dict()

        for section in PyObject.SECTION_ORDER:
            sections[section] = list()

        for name, bld_val in bld_obj['val']['val'].items():
            var = PyVariable(name, bld_val)
            sections['attrs'].append([var])

        col = basic.ComplexCollection(PyClass.COL_SET, bld_obj['val']['type_str'], sections, PyObject.SECTION_ORDER, PyObject.SECTION_REORDERABLE)

        basic.Container.__init__(self, bld_obj['type_str'], col)


class PyClass(basic.Container):
    COL_SET = basic.CollectionSettings(8, 8, 5, basic.CollectionSettings.VERTICAL)
    HIDDEN_VARS = {'__module__', '__dict__', '__weakref__', '__doc__'}
    SECTION_REORDERABLE = False

    def __init__(self, bld_class: 'python bld class', show_class_hidden_vars = False):
        if not PyClass.is_class(bld_class):
            raise TypeError(f'PyClass.__init__: {bld_class} is not a python bld class')

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


class PySceneCreator(SceneCreator):
    def __init__(self, bld_scene: 'python bld scene'):
        SceneCreator.__init__(bld_scene)

    def create_new_obj_with_id(bld_val: 'python bld value') -> PyValue:
        if PyPrimitive.is_primitive(bld_val):
            val = PyPrimitive(bld_val)
        elif PyCollection.is_collection(bld_val):
            val = PyCollection(bld_val)

        return val

    def create_primitive(bld_prim: 'python bld primitive') -> PyPrimitive:

    def create_scene(self) -> Scene:
        # bld_scene is a list of bld variables, so loop through the list and
        #   call create_new_value on each bld variable.
        pass


class PyScene(basic.Scene):
    def __init__(self, scene_bld: 'python bld scene'):
        vars = list()

        for name, bld_val in scene_bld.items():
            var = PyVariable(name, bld_val)
            vars.append(var)

        basic.Scene.__init__(self, vars)


class PySnapshot(basic.Snapshot):
    def __init__(self, globals_bld: 'python bld globals', locals_bld: 'python bld locals'):
        globals_scene = PyScene(globals_bld)
        locals_scene = PyScene(locals_bld)

        basic.Snapshot.__init__(self, OrderedDict([('globals', globals_scene), ('locals', locals_scene)]))
