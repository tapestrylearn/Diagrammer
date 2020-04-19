from types import MappingProxyType

# TODO: settings
show_hidden_class_attrs = False

class PyObject:
    directory = {}  # Track previously used IDs when creating PyObjects to ensure appropriate uniqueness

    def __init__(self, obj: object):
        # Don't directly initialize PyObjects -- always use the PyObject.make_for_obj factory function
        self._obj = obj
        self._type = type(obj)

        PyObject.directory[id(obj)] = self

    def get_type(self) -> type:
        return self._type

    def get_type_name(self) -> str:
        return self._type.__name__

    def export(self) -> dict:
        return {
            'type' : self.get_type_name(),
        }

    def get_obj(self) -> object:
        return self._obj

    @staticmethod
    def make_for_obj(obj: object) -> 'PyObject':
        if id(obj) in PyObject.directory:
            return PyObject.directory[id(obj)]
        else:
            if Instance.is_instance(obj):
                pyobj = Instance(obj)
            elif Collection.is_collection(obj):
                pyobj = Namespace(obj) if Namespace.is_namespace(obj) else Collection(obj)
            else:
                pyobj = Value(obj)

            return pyobj

    @staticmethod
    def clear_directory() -> None:
        PyObject.directory = {}


class Variable:
    def __init__(self, name: str, pyobj: PyObject):
        self._name = name
        self._pyobj = pyobj

    def __str__(self) -> str:
        # For testing/debugging
        return f'{self._pyobj.get_type_name()} {self._name} = {str(self._pyobj)}'

    def export(self) -> dict:
        json = dict()

        json['name'] = self._name
        json['pyobj'] = self._pyobj.export()
        # todo: add reference too

        return json

    def get_name(self) -> str:
        return self._name

    def get_pyobj(self) -> PyObject:
        return self._pyobj



class Value(PyObject):
    def __init__(self, value: 'primitive'):
        PyObject.__init__(self, value)

        if type(value) == str:
            self._text = f"'{str(value)}'"
        elif type(value) == range:
            # range(1, 5, 2)
            sections = str(value).split(',')

            if len(sections) == 2:
                self._text = f'{sections[0][6:]}:{sections[1][1:-1]}'
            elif len(sections) == 3:
                self._text = f'{sections[0][6:]}:{sections[1][1:]}:{sections[2][1:-1]}'
        else:
            self._text = str(value)

    def __str__(self) -> str:
        # For testing/debugging
        return f'{self._text}'

    def export(self) -> dict:
        json = dict()

        for key, value in PyObject.export(self).items():
            json[key] = value

        json['text'] = self._text
        # todo: position top and center text

        return json

    def get_text(self) -> str:
        return self._text

    @staticmethod
    def is_value(obj: object) -> bool:
        return obj == None or type(obj) in {int, float, bool, str}



class Collection(PyObject):
    LINEAR_COLLECTION_TYPES = {
        'ordered' : (list, tuple),
        'unordered' : (set),
    }
    MAP_COLLECTION_TYPES = (dict, types.MappingProxyType)

    def __init__(self, col: 'collection'):
        PyObject.__init__(self, col)

        self._variables = []

        for i, element in enumerate(col):
            if Collection.is_dict_like(col):
                var_name = element
                pyobj = PyObject.make_for_obj(col[element])
            else:
                var_name = '' if Collection.is_set_like(col) else f'{i}'
                pyobj = PyObject.make_for_obj(element)
            else:
                # throw some kind of exception
                pass

            variable = Variable(var_name, pyobj)

            self._variables.append(variable)

    def get_variables(self) -> [Variable]:
        return self._variables

    def export(self) -> dict:
        json = {}

        for key, value in PyObject.export(self).items():
            json[key] = value

        json['vars'] = [var.export() for var in self._variables]

        return json

    @staticmethod
    def is_collection(obj: object) -> bool:
        return Collection.is_linear_collection(obj) or Collection.is_mapping_collection(obj)

    @staticmethod
    def is_linear_collection(obj: object) -> bool:
        return any(isinstance(obj, type_partition) for type_partition in Collection.LINEAR_COLLECTION_TYPES.values())

    @staticmethod
    def is_unordered_linear_collection(obj: object) -> bool:
        return isinstance(obj, Collection.LINEAR_COLLECTION_TYPES['unordered'])

    @staticmethod
    def is_mapping_collection(obj: object) -> bool:
        return isinstance(obj, Collection.MAP_COLLECTION_TYPES)

    @staticmethod
    def is_dict_like(obj: object) -> bool:
        return isinstance(obj, dict) or isinstance(obj, type(MappingProxyType(dict())))

    @staticmethod
    def is_set_like(obj: object) -> bool:
        return isinstance(obj, set)


class Namespace(Collection):
    BLACKLIST = {'__weakref__', '__module__', '__doc__', '__dict__'}

    directory = set()

    def __init__(self, namespace: dict):
        Namespace.directory.add(id(namespace))
        Collection.__init__(self, namespace)

    def export(self) -> dict:
        json = dict()

        for key, value in Collection.export(self).items():
            if key == 'vars':
                if show_hidden_class_attrs:
                    json[key] = value
                else:
                    json[key] = [var_json for var_json in value if var_json['name'] not in Namespace.BLACKLIST]
            else:
                json[key] = value

        return json

    @staticmethod
    def is_namespace(obj: object) -> bool:
        return id(obj) in Namespace.directory


class Instance(PyObject):
    def __init__(self, instance: object):
        PyObject.__init__(self, instance)
        self.namespace = Namespace(instance.__dict__)

    def export(self) -> dict:
        json = dict()

        for key, value in PyObject.export(self).items():
            json[key] = value

        json['namespace'] = self.namespace.export()

        return json

    def get_namespace(self) -> dict:
        return self.namespace

    @staticmethod
    def is_instance(obj: object) -> bool:
        return hasattr(obj, '__dict__')


class Diagram:
    def __init__(self, name: str, namespace: 'namespace'):
        self._name = name
        self._variables = []

        for key, value in namespace.items():
            pyobj = PyObject.make_for_obj(value)
            var = Variable(key, pyobj)

            self._variables.append(var)

    def __str__(self) -> str:
        # For testing/debugging
        return '\n'.join(str(var) for var in self._variables)

    def get_name(self) -> str:
        return self._name

    def get_variables(self) -> [Variable]:
        return self._variables

    def export(self) -> dict:
        # not sure if we want to add a visual representation of the namespace itself, but i didn't do that here
        return [var.export() for var in self._variables]

    def _gps(self):
        # todo -- add initial gpa algorithm
        pass


class Snapshot:
    def __init__(self, globals_contents: dict, locals_contents: dict):
        self._globals = Diagram('globals', globals_contents)
        self._locals = Diagram('locals', locals_contents)

    def __str__(self) -> str:
        # For testing/debugging purposes
        return f'globals: {self._globals}\nlocals: {self._locals}'

    def get_diagram(self, path: str) -> Diagram:
        if path == 'locals':
            return self._locals
        else:
            # Path tree only applies to self._globals
            path_pieces = path.split(':')

            if path_pieces[0] == 'globals':
                child = self._globals

                for segment in path_pieces[1:]:
                    child = child.get_child(segment)

                return child

    def export(self) -> dict:
        return {
            'globals' : self._globals.export(),
            'locals' : self._locals.export(),
        }


TYPES = {PyObject, Variable, Value, Collection, Namespace, Instance, Diagram, Snapshot}
