from collections import OrderedDict, namedtuple
from random import random

# arrow stuff
SOLID = 'solid'
DASHED = 'dashed'
CENTER = 'center'
EDGE = 'edge'
HEAD = 'head'
TAIL = 'tail'

# shape stuff
NO_SHAPE = 'no_shape'
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

    def __init__(self, sections: {str: [[object]]}, section_order: [str], reorderable: bool, section_reorderable: bool):
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
    def __init__(self, arrow_type: str):
        self._tx = 0
        self._ty = 0
        self._hx = 0
        self._hy = 0
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

    def __init__(self, width: float, height: float, header: str, content: str, shape: str):
        SceneObject.__init__(self)
        self._width = width
        self._height = height
        self._header = header
        self._content = content
        self._shape = shape
        self._x = 0
        self._y = 0
        self._arrow = None

    def _calculate_edge_pos(self, angle: float) -> (float, float):
        pass
        # calculates the x and y of the edge based on the angle and the shape

    # I took out set_x and set_y because it's inefficient for
    # them to be building blocks of set_pos since we would have to calculate
    # edge pos twice and I can't see where they'd be used on their own

    def set_pos(self, x: float, y: float) -> None:
        self._x = x
        self._y = y

        # complicated stuff about setting arrow x and y if arrow isn't None

    def set_arrow(self, arrow: Arrow, arrow_pos: str, arrow_side: str) -> None:
        self._arrow = arrow
        self._arrow_pos = arrow_pos
        self._arrow_side = arrow_side

    def get_width(self) -> float:
        return self._width

    def get_height(self) -> float:
        return self._height

    def get_header(self) -> str:
        return self._header

    def get_content(self) -> str:
        return self._content

    def get_shape(self) -> str:
        return self._shape

    def get_x(self) -> float:
        return self._x

    def get_y(self) -> float:
        return self._y

    def get_pos(self) -> (float, float):
        return (self.get_x(), self.get_y())

    def get_arrow(self) -> Arrow:
        return self._arrow

    def export(self) -> 'json':
        json = SceneObject.export(self)

        add_json = {
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'header': self._header,
            'content': self._content,
            'shape': self._shape
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class Collection(BasicShape):
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

        BasicShape.__init__(self, width, height, type_str, '', Collection.SHAPE)

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
    def __init__(self, col_set: CollectionSettings, type_str: str, vars: [SceneObject], reorderable: bool):
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


class Container(BasicShape):
    H_MARGIN = 5
    V_MARGIN = 5
    SHAPE = ROUNDED_RECT

    def __init__(self, type_str: str, col: Collection):
        BasicShape.__init__(self, Container.H_MARGIN * 2 + col.get_width(), Container.V_MARGIN * 2 + col.get_height(), type_str, '', Container.SHAPE)
        self._col = col

    def get_col(self) -> Collection:
        return self._col


class SceneCreator:
    def __init__(self, bld_scene: 'bld scene'):
        self._bld_scene = bld_scene
        self._scene_objs = list()

    def add_arrow(self, head_obj: SceneObject, tail_obj: SceneObject, head_pos: str, tail_pos: str, arrow_type: str) -> None:
        arrow = Arrow(arrow_type)
        head_obj.set_arrow(arrow, head_pos, HEAD)
        tail_obj.set_arrow(arrow, tail_pos, TAIL)
        self._add_obj_without_id(arrow)

    def add_obj(self, obj: SceneObject) -> None:
        self._scene_objs.append(obj)

    def add_all_objs(self) -> None:
        pass


class Scene:
    def __init__(self, scene_objs: [SceneObject]):
        self._scene_objs = scene_objs

    def gps(self) -> None:
        pass

    def export(self) -> list:
        return [obj.export() for obj in self._scene_objs]


class Snapshot:
    def __init__(self, scenes: OrderedDict, output: str):
        self._scenes = scenes
        self._output = output

    def get_scenes(self) -> OrderedDict:
        return self._scenes

    def get_scene(self, name: str) -> Scene:
        return self._scenes[name]

    def get_output(self) -> str:
        return self._output

    def export(self):
        json = dict()

        for name, scene in self._scenes.items():
            json[name] = scene.export()

        json['output'] = self._output

        return json
