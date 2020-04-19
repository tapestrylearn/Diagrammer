class SceneObject:
    def __init__(self, width: float, height: float, header: str, content: str):
        self._width = width
        self._height = height
        self._header = header
        self._content = content
        self._x = 0
        self._y = 0

    def set_x(self, x: float) -> None:
        self._x = x

    def set_y(self, y: float) -> None:
        self._y = y

    def get_width(self) -> float:
        return self._width

    def get_height(self) -> float:
        return self._height

    def get_header(self) -> str:
        return self._header

    def get_content(self) -> str:
        return self._content

    def get_x(self) -> float:
        return self._x

    def get_y(self) -> float:
        return self._y


class Variable(SceneObject):
    SIZE = 50

    def __init__(self, name: str, type_name: str, header_gen: 'function', valuestr: str):
        SceneObject.__init__(self, Variable.SIZE, Variable.SIZE, header_gen(name, type_name))


class Pointer(Variable):
    def __init__(self, name: str, type_name: str, header_gen: 'function', head_obj: SceneObject):
        Variable.__init__(self, name, type_name, header_gen, '')

        self._head_obj = head_obj


class Reference(Pointer): # i made reference a subclass of pointer instead of variable
    pass


class VariableGroup(SceneObject):
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, base_var: [Variable], pointers: [Pointer], refs: [Reference], var_groups: [VariableGroup], dir: int, var_margin: float):
        total_len = 1 + len(pointers) + len(refs) + sum([len(group) for group in var_groups])
        short = Variable.SIZE
        long = var_margin * (len(self) - 1) + Variable.SIZE * len(self)

        SceneObject.__init__(self, short if dir == VERTICAL else long, long if dir == VERTICAL else short, '', '')

        self._base_var = base_var
        self._pointers = pointers
        self._refs = refs
        self._var_groups = var_groups
        self._dir = dir
        self._var_margin = var_margin
        self._total_len = total_len

    def __len__(self) -> int:
        return self._total_len

    def set_x(self, x: float) -> None:
        for (i, shape) in enumerate(self):
            if dir == VariableGroup.VERTICAL:
                shape.set_x(x)
            else:
                shape.set_x(x + (self._var_margin + Variable.SIZE) * i)

    def set_y(self, y: float) -> None:
        for (i, shape) in enumerate(self):
            if dir == VariableGroup.HORIZONTAL:
                shape.set_y(y)
            else:
                shape.set_y(y + (self._var_margin + Variable.SIZE) * i)

    def __iter__(self) -> (int, SceneObject):
        def gen_values() -> SceneObject:
            yield self._base_var

            start = 1

            for i in range(start, len(self._pointers) + start):
                yield self._pointers[i - start]

            start += len(self._pointers)

            for i in range(start, len(self._refs) + start):
                yield self._refs[i - start]

            start += len(self._refs)
            i = start

            for group in self._var_groups:
                yield group
                i += len(group)

        return gen_values()


class Value(SceneObject):
    pass


class BasicValue(Value):
    RADIUS = 25

    def __init__(self, type_name: str, valuestr: str):
        Value.__init__(self, Value.RADIUS * 2, Value.RADIUS * 2, type_name, valuestr)


# ordering rules for collections:
# ordered collections strictly follow their order (no groups)
# unordered collections have groups that are glued together but can move the groups around however they like
# basic vars and pointers don't have to be separated; they can be mixed
# the base variable in a variable group always remains on the left/top
class Collection(Value):
    def __init__(self, width: float, height: float, type_name: str):
        Value.__init__(self, width, height, type_name, '')


class OrderedCollection(Collection):
    H_MARGIN = 5
    V_MARGIN = 5

    def __init__(self, vars: [Variable], type_name: str):
        Collection.__init__(self, OrderedCollection.H_MARGIN * 2 + Variable.SIZE * len(vars), OrderedCollection.V_MARGIN * 2 + Variable.SIZE, type_name)
        
        self._vars = vars


class UnorderedCollection(Collection):
    H_MARGIN = OrderedCollection.H_MARGIN
    V_MARGIN = OrderedCollection.V_MARGIN
    # this doesn't have VAR_MARGIN = 0 because that would imply that you could set VAR_MARGIN to not be 0, which you're not allowed to do
    DIR = VariableGroup.HORIZONTAL # used for variable groups


class NamespaceCollection(Collection):
    H_MARGIN = 8
    V_MARGIN = 8
    VAR_MARGIN = 5 # used for variable groups
    DIR = VariableGroup.VERTICAL # used for variable groups

    # how variable groups are going to be used: there's going to be a list of VariableGroups which can be reordered (there are many ways to reorder but a simple example is a
    # reorder function that takes in two indices and swaps them)
    # when setx is called, it sets the x of all the variable groups accordingly, putting VAR_MARGIN of space between them


class Container(BasicShape):
    H_MARGIN = 5
    V_MARGIN = 5

    def __init__(self, type_name: str, attributes: Collection):
        BasicShape.__init__(self, Container.H_MARGIN * 2 + col.get_width(), Container.V_MARGIN * 2 + attributes.get_height(), type_name, '')
        self._attributes = attributes
