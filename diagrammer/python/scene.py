# notes for meeting: talk about valuefactory and testing export vs object (i think we should test object for language and export for general scene)

from ..scene import basic

PY_HEADER_GEN = lambda name, typestr : name


def is_type(bld_val: 'python bld value', type_obj: type) -> bool:
    return eval(f'isinstance({bld_val["typestr"]}(), {type_to_str(type_obj)})')

def type_to_str(type_obj: type) -> str:
    return str(type_obj)[8:-2]

def value_to_str(val: object) -> str:
    if type(val) is str:
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
            elif PyPrimitive.is_collection(bld_val):
                val = PyCollection(bld_val)

            PyFactory.directory[bld_val['id']] = val
            return val

    @staticmethod
    def clear_directory() -> None:
        PyFactory.directory = dict()


class PyPrimitive(basic.BasicValue):
    def __init__(self, bld_primval: 'python bld primitive value'):
        basic.BasicValue.__init__(self, bld_primval['typestr'], value_to_str(bld_primval['val']))

    @staticmethod
    def is_primitive(bld_val: 'python bld value'):
        return is_type(bld_val, int) or is_type(bld_val, str) or is_type(bld_val, float) or is_type(bld_val, bool)


class PyVariable(basic.Pointer):
    def __init__(self, name: str, bld_val: 'python bld value'):
        basic.Pointer.__init__(self, name, bld_val['typestr'], PY_HEADER_GEN, PyFactory.create_value(bld_val))


class PyCollection(basic.SimpleCollection):
    ORDERED_COL_SET = basic.CollectionSettings(5, 5, 0, basic.CollectionSettings.HORIZONTAL)
    UNORDERED_COL_SET = basic.CollectionSettings(5, 5, 2, basic.CollectionSettings.HORIZONTAL)

    def __init__(self, bld_col: 'python bld collection'):
        if not PyCollection.is_collection(bld_col):
            raise TypeError(f'PyCollection.__init__: {col} is not a python collection type')

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
                for key, bld_val in bld_col['val'].items():
                    var = PyVariable(key, bld_val)
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


class PyScene(basic.Scene):
    pass
