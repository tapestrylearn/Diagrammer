class SceneObject:
    def __init__(self, width: float, height: float):
        self._x = 0
        self._y = 0
        self._width = width
        self._height = height

    def set_x(self, x: float) -> None:
        self._x = x

    def set_y(self, y: float) -> None:
        self._y = y

    def get_x(self) -> float:
        return self._x

    def get_y(self) -> float:
        return self._y

    def get_width(self) -> float:
        return self._width

    def get_height(self) -> float:
        return self._height

    def export(self) -> dict:
        return {
            'x' : self._x,
            'y' : self._y,
            'width' : self._width,
            'height' : self._height,
        }


class PyObject:
    directory = dict()  # Track previously used IDs when creating PyObjects to ensure appropriate uniqueness

    def __init__(self, obj: object):
        # Don't directly initialize PyObjects -- always use the PyObject.make_for_obj factory function
        self._type = type(obj)
        PyObject.directory[id(obj)] = self

    def get_type(self) -> type:
        return self._type

    def get_typestr(self) -> str:
        return str(self._type)[8:-2]

    def export(self) -> dict:
        return {
            'type' : self.get_typestr(),
        }

    @staticmethod
    def make_for_obj(obj: object) -> 'PyObject':
        if id(obj) in PyObject.directory:
            return PyObject.directory[id(obj)]
        else:
            if Namespace.is_namespace(obj):
                pyobj = Namespace(obj)
            elif Collection.is_collection(obj):
                pyobj = Collection(obj)
            else:
                pyobj = Value(obj)

            return pyobj

    @staticmethod
    def clear_directory() -> None:
        PyObject.directory = dict()


class Variable(SceneObject):
    SIZE = 50

    def __init__(self, name: str, pyobj: PyObject):
        SceneObject.__init__(self, Variable.SIZE, Variable.SIZE)

        self._name = name
        self._pyobj = pyobj

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

    def __str__(self) -> str:
        return f'{self._name} -> {self._pyobj}'


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

    def export(self) -> dict:
        json = {}

        for key, value in SceneObject.export(self).items():
            json[key] = value

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


class Container(SceneObject):
    def __init__(self, col: 'collection', width: float, height: float):
        SceneObject.__init__(self, width, height)

        self._variables = []

        for i, element in enumerate(col):
            if isinstance(col, dict):
                key, value = list(col.items())[i]

                var_name = key
                pyobj = PyObject.make_for_obj(value)
            else:
                var_name = '' if isinstance(col, set) else f'{i}'
                pyobj = PyObject.make_for_obj(element)

            variable = Variable(var_name, pyobj)

            self._variables.append(variable)

    def get_variables(self) -> [Variable]:
        return self._variables

    def export(self) -> dict:
        json = {}

        for key, value in SceneObject.export(self).items():
            json[key] = value

        json['vars'] = [var.export() for var in self._variables]

        return json

    def set_x(self, x: float) -> None:
        SceneObject.set_x(self, x)
        self._position_elements()

    def set_y(self, y: float) -> None:
        SceneObject.set_y(self, y)
        self._position_elements()

    def _position_elements(self) -> None:
        pass

    def get_variables(self) -> [Variable]:
        return self._variables

    @staticmethod
    def is_container(obj: object) -> bool:
        return Namespace.is_namespace(obj) or Collection.is_collection(obj)


class Collection(PyObject, Container):
    H_MARGIN = 10
    V_MARGIN = 10

    def __init__(self, col: 'collection'):
        PyObject.__init__(self, col)

        Container.__init__(self, col,
            Collection.H_MARGIN * 2 + Variable.SIZE * len(col),
            Collection.V_MARGIN * 2 + Variable.SIZE
        )

    def _position_elements(self):
        for i in range(len(self._variables)):
            self._variables[i].set_x(self.get_x() + Collection.H_MARGIN + Variable.SIZE * i)
            self._variables[i].set_y(self.get_y() + Collection.V_MARGIN)

    def export(self) -> dict:
        json = {}

        for key, value in Container.export(self).items():
            json[key] = value

        for key, value in PyObject.export(self).items():
            json[key] = value

        return json

    @staticmethod
    def is_collection(obj: object) -> bool:
        col_types = (list, tuple, dict, set)
        return any(isinstance(obj, col_type) for col_type in col_types)


class Namespace(PyObject, Container):
    H_MARGIN = 20
    V_MARGIN = 20
    VAR_GAP = Variable.SIZE

    def __init__(self, namespace: 'namespace'):
        PyObject.__init__(self, namespace)

        col = namespace.__dict__

        Container.__init__(self, col,
            Collection.H_MARGIN * 2 + Variable.SIZE * len(col),
            Collection.V_MARGIN * 2 + Variable.SIZE
        )

    def _position_elements(self):
        for i in range(len(self._variables)):
            self._variables[i].set_x(self.get_x() + Namespace.H_MARGIN)
            self._variables[i].set_y(self.get_y() + Namespace.V_MARGIN + (Variable.SIZE + Namespace.VAR_GAP) * i)

    def export(self) -> dict:
        json = {}

        for key, value in Container.export(self).items():
            json[key] = value

        for key, value in PyObject.export(self).items():
            json[key] = value

        return json

    @staticmethod
    def is_namespace(obj: object) -> bool:
        return hasattr(obj, '__dict__')


class Diagram:
    def __init__(self, name: str, ddict: dict):
        self._name = name

        self._variables = []
        self._children = []

        for name, value in ddict:
            pyobj = PyObject.make_for_obj(value)
            var = Variable(name, pyobj)

            self._variables.append(var)

    def get_name(self) -> str:
        return self._name

    def get_variables(self) -> [Variable]:
        return self._variables

    def get_children(self) -> ['Diagram']:
        return self._children

    def get_child(self, name: str) -> 'Diagram':
        for child in self._children:
            if child.get_name() == name:
                return child

    def export(self) -> dict:
        # not sure if we want to add a visual representation of the namespace itself, but i didn't do that here
        return {
            'diagram' : [var.export() for var in self._variables],
            'children' : [child.export() for child in self._children],
        }

    def _gps(self):
        # todo -- add initial gpa algorithm
        pass


class Snapshot:
    def __init__(self, globals_contents: dict, locals_contents: dict):
        self._globals = Diagram('globals', globals_contents)
        self._locals = Diagram('locals', locals_contents)

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

    def generate_path_tree(self) -> dict:
        # Recursive helper method for generating path trees
        def generate_path_tree_from_root(root: Diagram) -> dict:
            return {
                child.name : (generate_path_tree_from_root(child) for child in root.get_children()) if len(root.get_children()) > 0 else None,
            }

        return {
            'globals' : generate_path_tree_from_root(self._globals),
            'locals' : generate_path_tree_from_root(self._locals),
        }

    def export(self) -> dict:
        return {
            'globals' : self._globals.export(),
            'locals' : self._locals.export(),
            'paths' : self.generate_path_tree(),
        }


TYPES = {SceneObject, PyObject, Variable, Value, Container, Diagram, Snapshot}
