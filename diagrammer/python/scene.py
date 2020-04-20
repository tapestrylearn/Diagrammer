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


class Value(BasicShape):
    pass


class BasicValue(Value):
    RADIUS = 25

    def __init__(self, typestr: str, valuestr: str):
        Value.__init__(self, Value.RADIUS * 2, Value.RADIUS * 2, typestr, valuestr)


class Collection(Value):
    def __init__(self, col_set: CollectionSettings, typestr: str, sections: {str: [[Variable]]}, section_order: [str]):
        total_len = sum([sum([len(group) for group in groups]) for groups in sections.items()])

        if col_set.dir == CollectionSettings.HORIZONTAL:
            width = col_set.hmargin * 2 + col_set.var_margin * (total_len - 1) + Variable.SIZE * total_len
            height = col_set.vmargin * 2 + Variable.SIZE
        else:
            width = col_set.hmargin * 2 + Variable.SIZE
            height = col_set.vmargin * 2 + col_set.var_margin * (total_len - 1) + Variable.SIZE * total_len

        Value.__init__(self, width, height, typestr, '')

        self._sections = sections
        self._section_order = section_order
        self._col_set = col_set

    def set_x(self, x: float) -> None:
        Value.set_x(self, x)

        for (i, var) in enumerate(self):
            if self._col_set.dir == CollectionSettings.VERTICAL:
                var.set_x(self._col_set.hmargin + x)
            else:
                var.set_x(self._col_set.hmargin + x + (Variable.SIZE + self._col_set.var_margin) * i)

    def set_y(self, y: float) -> None:
        Value.set_y(self, y)

        for (i, var) in enumerate(self):
            if self._col_set.dir == CollectionSettings.VERTICAL:
                var.set_y(self._col_set.vmargin + y)
            else:
                var.set_y(self._col_set.vmargin + y + (Variable.SIZE + self._col_set.var_margin) * i)

    def reorder(self, section: str, i: int, j: int) -> None:
        self._sections[section][i], self._sections[section][j] = self._sections[section][j], self._sections[section][i]

    def __iter__(self) -> Variable:
        for section in section_order:
            for group in sections[section]:
                for var in group:
                    yield var

# example python specific implementation of collection
class PyCollection(Collection):
    HMARGIN = 5
    VMARGIN = 5
    VAR_MARGIN = 0
    DIR = CollectionSettings.HORIZONTAL

    def __init__(self, typestr: str, pointers: [Pointer]):
        group = list()
        group[0] = pointers

        sections = {
            'pointers': group
        }

        section_order = ['pointers']
        Collection.__init__(self, CollectionSettings(hmargin, vmargin, var_margin, dir), typestr, sections, section_order)
        self._pointers = pointers


class CollectionSettings:
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, hmargin: float, vmargin: float, var_margin: float, dir: int):
        self.hmargin = hmargin
        self.vmargin = vmargin
        self.var_margin = var_margin
        self.dir = dir


class Container(BasicShape):
    H_MARGIN = 5
    V_MARGIN = 5

    def __init__(self, typestr: str, col: Collection):
        BasicShape.__init__(self, Container.H_MARGIN * 2 + col.get_width(), Container.V_MARGIN * 2 + col.get_height(), typestr, '')
        self._col = col
