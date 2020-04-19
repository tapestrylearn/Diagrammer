import types

class SceneObject:
    def __init__(self, width: float, height: float):
        self._x = 0
        self._y = 0
        self._width = width
        self._height = height

    def get_x(self) -> float:
        return self._x

    def get_y(self) -> float:
        return self._y

    def set_x(self, x: float) -> None:
        self._x = x

    def set_y(self, y: float) -> None:
        self._y = y

    def set_pos(self, x: float, y: float) -> None:
        self.set_x(x)
        self.set_y(y)

    def get_width(self) -> float:
        return self._width

    def get_height(self) -> float:
        return self._height

    def set_width(self, width: float) -> None:
        self._width = width

    def set_height(self, height: float) -> None:
        self._height = height

    def set_size(self, width: float, height: float) -> None:
        self.set_width(width)
        self.set_height(height)

    def export(self) -> dict:
        return {
            'x' : self._x,
            'y' : self._y,
            'width' : self._width,
            'height' : self._height,
        }



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
                pyobj = StdCollection(obj) if not Namespace.exists_for(obj) else Namespace(obj)
            else:
                pyobj = Value(obj)

            return pyobj

    @staticmethod
    def clear_directory() -> None:
        PyObject.directory = {}


class Variable(SceneObject):
    SIZE = 50

    def __init__(self, name: str, pyobj: PyObject):
        SceneObject.__init__(self, Variable.SIZE, Variable.SIZE)

        self._name = name
        self._pyobj = pyobj

    def __str__(self) -> str:
        # For testing/debugging
        return f'{self._pyobj.get_type_name()} {self._name} = {str(self._pyobj)}'

    def export(self) -> dict:
        json = SceneObject.export(self)

        json['name'] = self._name
        json['pyobj'] = self._pyobj.export()
        # todo: add reference too

        return json

    def get_name(self) -> str:
        return self._name

    def get_pyobj(self) -> PyObject:
        return self._pyobj



class Value(PyObject, SceneObject):
    RADIUS = 25

    def __init__(self, value: 'primitive'):
        PyObject.__init__(self, value)
        SceneObject.__init__(self, Value.RADIUS * 2, Value.RADIUS * 2)

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
        json = {}

        for key, value in PyObject.export(self).items():
            json[key] = value

        for key, value in SceneObject.export(self).items():
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
            if Collection.is_mapping_collection(col):
                var_name = element
                pyobj = PyObject.make_for_obj(col[element])
            elif Collection.is_linear_collection(col):
                var_name = '' if Collection.is_unordered_linear_collection(col) else f'{i}'
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


class StdCollection(Collection, SceneObject):
    H_MARGIN = 10
    V_MARGIN = 10

    def __init__(self, stdcol: 'primitive collection'):
        Collection.__init__(self, stdcol)
        SceneObject.__init__(self,
            StdCollection.H_MARGIN * 2 + Variable.SIZE * len(stdcol),
            StdCollection.V_MARGIN * 2 + (Variable.SIZE if len(stdcol) > 0 else 0)
        )

    def set_x(self, x: float) -> None:
        SceneObject.set_x(self, x)

        for i in range(len(self._variables)):
            self._variables[i].set_x(x + StdCollection.H_MARGIN + Variable.SIZE * i)

    def set_y(self, y: float) -> None:
        SceneObject.set_y(self, y)

        for i in range(len(self._variables)):
            self._variables[i].set_y(y + StdCollection.V_MARGIN)

    def export(self) -> dict:
        json = {}

        for key, value in Collection.export(self).items():
            json[key] = value

        for key, value in SceneObject.export(self).items():
            json[key] = value

        return json


class Namespace(Collection, SceneObject):
    H_MARGIN = 20
    V_MARGIN = 20
    VAR_GAP = Variable.SIZE
    BLACKLIST = {'__weakref__', '__module__', '__doc__', '__dict__'}

    directory = set()

    def __init__(self, namespace: dict):
        Namespace.directory.add(id(namespace))

        Collection.__init__(self, namespace)
        SceneObject.__init__(self,
            Namespace.H_MARGIN * 2 + (Variable.SIZE if len(namespace) > 0 else 0),
            Namespace.V_MARGIN * 2 + Variable.SIZE * len(namespace) + Namespace.VAR_GAP * max(0, len(namespace) - 1)
        )

    def set_x(self, x: float) -> None:
        SceneObject.set_x(self, x)

        for i in range(len(self._variables)):
            self._variables[i].set_x(x + Namespace.H_MARGIN)

    def set_y(self, y: float) -> None:
        SceneObject.set_y(self, y)

        for i in range(len(self._variables)):
            self._variables[i].set_y(y + Namespace.V_MARGIN + (Variable.SIZE + Namespace.VAR_GAP) * i)

    def export(self) -> dict:
        json = {}

        for key, value in Collection.export(self).items():
            json[key] = value

        to_delete = []

        for i, var in enumerate(json['vars']):
            if var['name'] in Namespace.BLACKLIST:
                to_delete.append(i)

        for offset, index in enumerate(to_delete):
            del json['vars'][i - offset]

        self.set_size(
            Namespace.H_MARGIN * 2 + (Variable.SIZE if len(json['vars']) > 0 else 0),
            Namespace.V_MARGIN * 2 + Variable.SIZE * len(json['vars']) + Namespace.VAR_GAP * max(0, len(json['vars']) - 1)
        )

        for key, value in SceneObject.export(self).items():
            json[key] = value

        return json

    @staticmethod
    def exists_for(obj: object) -> bool:
        return id(obj) in Namespace.directory


class Instance(PyObject, SceneObject):
    H_MARGIN = 5
    V_MARGIN = 5

    def __init__(self, instance: object):
        PyObject.__init__(self, instance)
        # print('hi', instance.__dict__)

        # namespace = {key: val for key, val in instance.__dict__.items() if key not in Namespace.BLACKLIST}
        namespace = instance.__dict__ # weird bug #1 -- fixed bc blacklisting creates new dict, so IDs don't match and duplicates aren't caught
        self.namespace = Namespace(namespace)
        
        SceneObject.__init__(self,
            Instance.H_MARGIN * 2 + self.namespace.get_width(),
            Instance.V_MARGIN * 2 + self.namespace.get_height()
        )

    def export(self) -> dict:
        json = {}

        for key, value in PyObject.export(self).items():
            json[key] = value

        for key, value in SceneObject.export(self).items():
            json[key] = value

        json['namespace'] = self.namespace.export()

        return json

    def get_namespace(self) -> dict:
        return self.namespace

    def set_x(self, x: float) -> None:
        SceneObject.set_x(self, x)

        self.namespace.set_x(x + Instance.H_MARGIN)

    def set_y(self, y: float) -> None:
        SceneObject.set_y(self, y)

        self.namespace.set_y(y + Instance.V_MARGIN)

    @staticmethod
    def is_instance(obj: object) -> bool:
        return hasattr(obj, '__dict__')


class Diagram:
    def __init__(self, name: str, namespace: 'namespace'):
        self._name = name
        self._variables = []

        for name, value in namespace.items():
            pyobj = PyObject.make_for_obj(value)
            var = Variable(name, pyobj)

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


TYPES = {SceneObject, PyObject, Variable, Value, Collection, StdCollection, Namespace, Instance, Diagram, Snapshot}
