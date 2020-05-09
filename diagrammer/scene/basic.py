from collections import OrderedDict, namedtuple
from random import random

NO_SHAPE = 'no_shape'
SOLID = 'solid'
DASHED = 'dashed'
CIRCLE = 'circle'
SQUARE = 'square'
ROUNDED_RECT = 'rounded_rect'

class CollectionSettings:
    Direction = int

    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, hmargin: float, vmargin: float, var_margin: float, dir: Direction):
        self.hmargin = hmargin
        self.vmargin = vmargin
        self.var_margin = var_margin
        self.dir = dir


class ReorderException(Exception):
    pass


class SectionStructure:
    # TODO: add functions for creating an empty SectionStructure and modifying it like a dict of list of lists

    def __init__(self, sections: {str: [[object]]}, section_order, reorderable: bool, section_reorderable: bool):
        self._sections = sections
        self._section_order = section_order
        self._reorderable = reorderable
        self._section_reorderable = section_reorderable

    def get_sections(self) -> {str: [[Variable]]}:
        return self._sections

    def get_section_order(self) -> [str]:
        return self._section_order

    def get_reorderable(self) -> bool:
        return self._reorderable

    def get_section_reorderable(self) -> bool:
        return self._section_reorderable

    def reorder(self, section: str, i: int, j: int) -> None:
        if self._reorderable:
            self._sections[section][i], self._sections[section][j] = self._sections[section][j], self._sections[section][i]
        else:
            raise ReorderException()

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


class SceneObject:
    def export(self) -> 'json':
        return dict()


class Arrow(SceneObject):
    def __init__(self, tx: float, ty: float, hx: float, hy: float, arrow_type: str):
        self._tx = hx
        self._ty = hy
        self._hx = tx
        self._hy = ty
        self._arrow_type = arrow_type

    def export(self) -> 'json':
        json = SceneObject.export(self)

        add_json = {
            'tx': self._tx,
            'ty': self._ty,
            'hx': self._hx,
            'hy': self._hy,
            'arrow_type': self._arrow_type
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class BasicShape(SceneObject):
    SHAPE = NO_SHAPE

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

    def get_x(self) -> float:
        return self._x

    def get_y(self) -> float:
        return self._y

    def get_pos(self) -> (float, float):
        return (self.get_x(), self.get_y())

    def get_width(self) -> float:
        return self._width

    def get_height(self) -> float:
        return self._height

    def get_header(self) -> str:
        return self._header

    def get_content(self) -> str:
        return self._content

    def get_shape(self) -> str:
        return self.SHAPE

    def export(self) -> 'json':
        json = SceneObject.export(self)

        add_json = {
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'header': self._header,
            'content': self._content,
            'shape': self.SHAPE
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class Value(BasicShape):
    pass


class Variable(Value):
    SIZE = 50
    SHAPE = SQUARE

    def __init__(self, header: str, content: str):
        BasicShape.__init__(self, Variable.SIZE, Variable.SIZE, header, content)


class Pointer(Variable):
    ARROW_TYPE = SOLID

    def __init__(self, header: str, head_obj: SceneObject, factory: Factory):
        Variable.__init__(self, header, '')

        self._head_obj = head_obj
        self._arrow = Arrow(self.get_x(), self.get_y(), self._head_obj.get_x(), self._head_obj.get_y(), self.ARROW_TYPE)
        factory.get_other_scene_objects().append(self._arrow)

    def get_head_obj(self) -> SceneObject:
        return self._head_obj

    def export(self) -> 'json':
        json = Variable.export(self)

        return json


class Reference(Pointer):
    ARROW_TYPE = DASHED


class BasicValue(Value):
    RADIUS = 25
    SHAPE = CIRCLE

    def __init__(self, type_str: str, value_str: str):
        Value.__init__(self, BasicValue.RADIUS * 2, BasicValue.RADIUS * 2, type_str, value_str)


class Collection(Value):
    SHAPE = ROUNDED_RECT

    def __init__(self, col_set: CollectionSettings, type_str: str, total_len: int):
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

        Value.__init__(self, width, height, type_str, '')

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
            if self._col_set.dir == CollectionSettings.HORIZONTAL:
                var.set_y(self._col_set.vmargin + y)
            else:
                var.set_y(self._col_set.vmargin + y + (Variable.SIZE + self._col_set.var_margin) * i)

    def __iter__(self) -> Variable:
        return iter(self._vars)


class SimpleCollection(Collection):
    def __init__(self, col_set: CollectionSettings, type_str: str, vars: [Variable], reorderable: bool):
        Collection.__init__(self, col_set, type_str, len(vars))

        self._vars = vars
        self._reorderable = reorderable

    def reorder(self, i: int, j: int) -> None:
        if self._reorderable:
            self._vars[i], self._vars[j] = self._vars[j], self._vars[i]
        else:
            raise ReorderException()

    def get_vars(self) -> [Variable]:
        return self._vars


class ComplexCollection(Collection):
    def __init__(self, col_set: CollectionSettings, type_str: str, sect_struct: SectionStructure):
        total_len = sum([sum([len(group) for group in groups]) for groups in sections.items()])

        Collection.__init__(self, col_set, type_str, total_len)

        self._vars = sect_struct

    def get_sect_struct(self) -> SectionStructure:
        return self._vars


class Container(Value):
    H_MARGIN = 5
    V_MARGIN = 5
    SHAPE = ROUNDED_RECT

    def __init__(self, type_str: str, col: Collection):
        Value.__init__(self, Container.H_MARGIN * 2 + col.get_width(), Container.V_MARGIN * 2 + col.get_height(), type_str, '')
        self._col = col

    def get_col(self) -> Collection:
        return self._col


class SceneCreator:
    def __init__(self, bld_scene: 'bld scene'):
        self._values = dict()
        self._other_scene_objs = list()
        self._bld_scene = bld_scene
        self._sect_struct = SectionStructure()
        self.create_scene()

    def create_value(self, bld_value: 'bld value') -> Value:
        if bld_value['id'] in self._values:
            return self._values[bld_value['id']]
        else:
            value = create_new_value(self, bld_value: 'bld')
            self._values[bld_value['id']] = value
            return value

    def create_new_value(self, bld: 'bld value') -> Value:
        pass

    def create_scene(self) -> Scene:
        pass

    def get_sect_struct(self) -> SectionStructure:
        return self._sect_struct

    def add_other_scene_objs(self, other_scene_obj: SceneObject) -> None:
        self._other_scene_objs.append(other_scene_obj)


class PySceneCreator(SceneCreator):
    def __init__(self, bld_scene: 'python bld scene'):
        SceneCreator.__init__(bld_scene)

    def create_new_value(self, bld: 'bld value') -> Value:
        # standard python create new value function
        # this takes care of adding arrows to _other_scene_objs and adding the values to _sect_struct
        pass

    def create_scene(self) -> Scene:
        # bld_scene is a list of bld variables, so loop through the list and
        #   call create_new_value on each bld variable.
        pass


class Scene:
    # sect struct is for reordering, scene_objects is for export
    def __init__(self, sect_struct: SectionStructure, scene_objs: [SceneObject]):
        self._sect_struct = sect_struct
        self._scene_objs = scene_objs

    def get_sect_struct(self) -> SectionStructure:
        return self._sect_struct

    def gps(self) -> None:
        pass

    def export(self) -> list:
        return [obj.export() for obj in self._scene_objs]


class Snapshot:
    def __init__(self, scenes: OrderedDict):
        self._scenes = scenes

    def get_scenes(self) -> OrderedDict:
        return self._scenes

    def get_scene(self, name: str) -> Scene:
        return self._scenes[name]

    def export(self):
        json = dict()

        for name, scene in self._scenes.items():
            json[name] = scene.export()

        return json
