class SceneObject:
    pass


class BasicShape(SceneObject):
    def __init__(self, width: float, height: float, header: str, content: str):
        SceneObject.__init__(self)
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


class Variable(BasicShape):
    SIZE = 50

    def __init__(self, name: str, typestr: str, header_gen: lambda, valuestr: str):
        BasicShape.__init__(self, Variable.SIZE, Variable.SIZE, header_gen(name, typestr))


class BasicVariable(Variable):
    pass


class Pointer(Variable):
    def __init__(self, name: str, typestr: str, header_gen: lambda, headobj: SceneObject):
        Variable.__init__(self, name, typestr, header_gen, '')
        self._headobj = headobj


class Reference(Pointer): # i made reference a subclass of pointer instead of variable
    pass


class VariableGroup(BasicShape):
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, base_var: [Variable], pointers: [Pointer], refs: [Reference], var_groups: [VariableGroup], dir: int, var_margin: float):
        total_len = 1 + len(pointers) + len(refs) + sum([len(group) for group in var_groups])
        short = Variable.SIZE
        long = var_margin * (len(self) - 1) + Variable.SIZE * len(self)

        BasicShape.__init__(self, short if dir == VERTICAL else long, long if dir == VERTICAL else short, '', '')

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
        for (i, shape) in self._gen_next_item():
            if dir == VariableGroup.VERTICAL:
                shape.set_x(x)
            else:
                shape.set_x(x + (self._var_margin + Variable.SIZE) * i)

    def set_y(self, y: float) -> None:
        for (i, shape) in self._gen_next_item():
            if dir == VariableGroup.HORIZONTAL:
                shape.set_y(y)
            else:
                shape.set_y(y + (self._var_margin + Variable.SIZE) * i)

    def _gen_next_item(self) -> (int, BasicShape)
        yield (0, self._base_var)

        start = 1

        for i in range(start, len(self._pointers) + start):
            yield (i, self._pointers[i - start])

        start += len(self._pointers)

        for i in range(start, len(self._refs) + start):
            yield (i, self._refs[i - start])

        start += len(self._refs)
        i = start

        for group in self._var_groups:
            yield (i, group)
            i += len(group)


class Value(BasicShape):
    pass


class BasicValue(Value):
    RADIUS = 25

    def __init__(self, typestr: str, valuestr: str):
        Value.__init__(self, Value.RADIUS * 2, Value.RADIUS * 2, typestr, valuestr)


# ordering rules for collections:
# ordered collections strictly follow their order (no groups)
# unordered collections have groups that are glued together but can move the groups around however they like
# basic vars and pointers don't have to be separated; they can be mixed
# the base variable in a variable group always remains on the left/top
class Collection(Value):
    def __init__(self, width: float, height: float, typestr: str):
        Value.__init__(self, width, height, typestr, '')


class OrderedCollection(Collection):
    H_MARGIN = 5
    V_MARGIN = 5

    def __init__(self, vars: [Variable], typestr: str):
        Collection.__init__(OrderedCollection.H_MARGIN * 2 + Variable.SIZE * len(vars), OrderedCollection.V_MARGIN * 2 + Variable.SIZE, typestr)
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


class Container(BasicShape):
    H_MARGIN = 5
    V_MARGIN = 5

    def __init__(self, typestr: str, col: Collection):
        BasicShape.__init__(self, Container.H_MARGIN * 2 + col.get_width(), Container.V_MARGIN * 2 + col.get_height(), typestr, '')
        self._col = col
