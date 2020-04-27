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

    def set_pos(self, x: float, y: float) -> None:
        self.set_x(x)
        self.set_y(y)

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

    def get_pos(self) -> (float, float):
        return (self.get_x(), self.get_y())


class Variable(BasicShape):
    SIZE = 50

    def __init__(self, name: str, typestr: str, header_gen: 'function', valuestr: str):
        BasicShape.__init__(self, Variable.SIZE, Variable.SIZE, header_gen(name, typestr), valuestr)


class Pointer(Variable):
    def __init__(self, name: str, typestr: str, header_gen: 'function', head_obj: SceneObject):
        Variable.__init__(self, name, typestr, header_gen, '')

        self._head_obj = head_obj

    def get_head_obj(self) -> SceneObject:
        return self._head_obj


class Reference(Pointer):
    def __init__(self, name: str, typestr: str, header_gen: 'function', head_obj: Variable):
        Pointer.__init__(self, name, typestr, header_gen, head_obj)


class Value:
    pass


class BasicValue(BasicShape, Value):
    RADIUS = 25

    def __init__(self, typestr: str, valuestr: str):
        Value.__init__(self)
        BasicShape.__init__(self, BasicValue.RADIUS * 2, BasicValue.RADIUS * 2, typestr, valuestr)


class CollectionSettings:
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, hmargin: float, vmargin: float, var_margin: float, dir: int):
        self.hmargin = hmargin
        self.vmargin = vmargin
        self.var_margin = var_margin
        self.dir = dir


class ReorderException(Exception):
    pass


class Collection(BasicShape, Value):
    def __init__(self, col_set: CollectionSettings, typestr: str, total_len: int):
        Value.__init__(self)

        if total_len == 0:
            width = col_set.hmargin * 2
            height = col_set.vmargin * 2
        else:
            if col_set.dir == CollectionSettings.HORIZONTAL:
                width = col_set.hmargin * 2 + col_set.var_margin * (total_len - 1) + Variable.SIZE * total_len
                height = col_set.vmargin * 2 + Variable.SIZE
            else:
                width = col_set.hmargin * 2 + Variable.SIZE
                height = col_set.vmargin * 2 + col_set.var_margin * (total_len - 1) + Variable.SIZE * total_len

        BasicShape.__init__(self, width, height, typestr, '')

        self._col_set = col_set

    def set_x(self, x: float) -> None:
        BasicShape.set_x(self, x)

        for (i, var) in enumerate(self):
            if self._col_set.dir == CollectionSettings.VERTICAL:
                var.set_x(self._col_set.hmargin + x)
            else:
                var.set_x(self._col_set.hmargin + x + (Variable.SIZE + self._col_set.var_margin) * i)

    def set_y(self, y: float) -> None:
        BasicShape.set_y(self, y)

        for (i, var) in enumerate(self):
            if self._col_set.dir == CollectionSettings.HORIZONTAL:
                var.set_y(self._col_set.vmargin + y)
            else:
                var.set_y(self._col_set.vmargin + y + (Variable.SIZE + self._col_set.var_margin) * i)


class SimpleCollection(Collection):
    def __init__(self, col_set: CollectionSettings, typestr: str, vars: [Variable], reorderable: bool):
        Collection.__init__(self, col_set, typestr, len(vars))

        self._vars = vars
        self._reorderable = reorderable

    def reorder(self, i: int, j: int) -> None:
        if self._reorderable:
            self._vars[i], self._vars[j] = self._vars[j], self._vars[i]
        else:
            raise ReorderException()

    def get_vars(self) -> [Variable]:
        return self._vars

    def __iter__(self) -> Variable:
        for var in self._vars:
            yield var


class ComplexCollection(Collection):
    def __init__(self, col_set: CollectionSettings, typestr: str, sections: {str: [[Variable]]}, section_order: [str], section_reorderable: bool):
        total_len = sum([sum([len(group) for group in groups]) for groups in sections.items()])

        Collection.__init__(self, col_set, typestr, total_len)

        self._sections = sections
        self._section_order = section_order
        self._section_reorderable = section_reorderable

    def reorder(self, section: str, i: int, j: int) -> None:
        self._sections[section][i], self._sections[section][j] = self._sections[section][j], self._sections[section][i]

    def reorder_ml(self, section_index: int, i: int, j: int) -> None:
        self.reorder(self._section_order[section_index], i, j)

    def reorder_section(self, i: int, j: int) -> None:
        if self._section_reorderable:
            self._section_order[i], self._section_order[j] = self._section_order[j], self._section_order[i]
        else:
            raise ReorderException()

    def __iter__(self) -> Variable:
        for section in self._section_order:
            for group in self._sections[section]:
                for var in group:
                    yield var


class Container(BasicShape):
    H_MARGIN = 5
    V_MARGIN = 5

    def __init__(self, typestr: str, col: Collection):
        BasicShape.__init__(self, Container.H_MARGIN * 2 + col.get_width(), Container.V_MARGIN * 2 + col.get_height(), typestr, '')
        self._col = col

    def get_col(self) -> Collection:
        return self._col


class Scene:
    def __init__(self, width, height, objects: [SceneObject]):
        self._width = width
        self._height = height
        self._objects = objects

    def get_objects(self) -> SceneObject:
        return self._scene_object
