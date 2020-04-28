# notes for meeting: talk about valuefactory and testing export vs object (i think we should test object for language and export for general scene)

from ..scene import basic

PY_HEADER_GEN = lambda name, typestr : name


def is_type(bld_val: 'python bld value', type_obj: type) -> bool:
    return eval(f'isinstance({bld_val["typestr"]}(), {type_to_str(type_obj)})')

def type_to_str(type_obj: type) -> str:
    return str(type_obj)[8:-2]

def value_to_str(typestr: str, val: object) -> str:
    if typestr == 'str':
        return f"'{val}'"
    else:
        return str(val)


# the reason this isn't a class in basic is that it's implemented differently in different languages
# in python, for example, this only creates values, but in c++ it can also create variables
class PyFactory:
    directory = dict()

    @staticmethod
    def create_value(bld_val) -> basic.Value:
        if bld_val['id'] in PyFactory.directory:
            return PyFactory.directory[bld_val['id']]
        else:
            if PyPrimitive.is_primitive(bld_val):
                val = PyPrimitive(bld_val)
            elif PyCollection.is_collection(bld_val):
                val = PyCollection(bld_val)

            PyFactory.directory[bld_val['id']] = val
            return val

    @staticmethod
    def clear_directory() -> None:
        PyFactory.directory = dict()


class PyPrimitive(basic.BasicValue):
    PRIMITIVE_TYPESTRS = {'int', 'str', 'float', 'bool', 'function', 'NoneType'}

    def __init__(self, bld_prim: 'python bld primitive'):
        if not PyPrimitive.is_primitive(bld_prim):
            raise TypeError(f'PyPrimitive.__init__: {col} is not a python bld primitive')

        basic.BasicValue.__init__(self, bld_prim['typestr'], value_to_str(bld_prim['typestr'], bld_prim['val']))

    @staticmethod
    def is_primitive(bld_val: 'python bld value'):
        return bld_val['typestr'] in PyPrimitive.PRIMITIVE_TYPESTRS


class PyVariable(basic.Pointer):
    def __init__(self, name: str, bld_val: 'python bld value'):
        basic.Pointer.__init__(self, name, bld_val['typestr'], PY_HEADER_GEN, PyFactory.create_value(bld_val))


class PyCollection(basic.SimpleCollection):
    ORDERED_COL_SET = basic.CollectionSettings(5, 5, 0, basic.CollectionSettings.HORIZONTAL)
    UNORDERED_COL_SET = basic.CollectionSettings(5, 5, 2, basic.CollectionSettings.HORIZONTAL)

    def __init__(self, bld_col: 'python bld collection'):
        if not PyCollection.is_collection(bld_col):
            raise TypeError(f'PyCollection.__init__: {col} is not a python bld collection')

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

        basic.SimpleCollection.__init__(self, col_set, bld_col['typestr'], vars, reorderable)

    @staticmethod
    def is_collection(bld_val: 'python bld value') -> bool:
        return PyCollection.is_ordered_collection(bld_val) or PyCollection.is_unordered_collection(bld_val)

    @staticmethod
    def is_ordered_collection(bld_val: 'python bld value') -> bool:
        return is_type(bld_val, list) or is_type(bld_val, tuple)

    @staticmethod
    def is_unordered_collection(bld_val: 'python bld value') -> bool:
        return is_type(bld_val, set) or is_type(bld_val, dict)


class PyClass(basic.Container):
    COL_SET = basic.CollectionSettings(8, 8, 5, basic.CollectionSettings.VERTICAL)
    HIDDEN_VARS = {'__module__', '__dict__', '__weakref__', '__doc__'}
    SECTION_REORDERABLE = False

    def __init__(self, bld_class: 'python bld class', show_class_hidden_vars = False):
        if not PyClass.is_class(bld_class):
            raise TypeError(f'PyClass.__init__: {col} is not a python bld class')

        if not show_class_hidden_vars:
            section_order = ['attrs', 'methods']
        else:
            section_order = ['hidden', 'attrs', 'methods']

        sections = dict()

        for section in section_order:
            sections[section] = list()

        for name, bld_val in bld_class['val']['__dict__']['val'].items():
            if not show_class_hidden_vars and name in PyClass.HIDDEN_VARS:
                continue

            if name in PyClass.HIDDEN_VARS:
                section = 'hidden'
            elif bld_val['typestr'] == 'function':
                section = 'methods'
            else:
                section = 'attrs'

            var = PyVariable(name, bld_val)
            sections[section].append([var])

        col = basic.ComplexCollection(PyClass.COL_SET, bld_class['val']['__dict__']['typestr'], sections, section_order, PyClass.SECTION_REORDERABLE)

        basic.Container.__init__(self, bld_class['typestr'], col)

    @staticmethod
    def is_class(bld_val: 'python bld value'):
        return bld_val['typestr'] == 'type'


class PyScene(basic.Scene):
    pass
