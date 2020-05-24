from collections import OrderedDict, namedtuple
from random import random


class Shape:
    Type = str # shape option type alias

    NO_SHAPE = 'no_shape'
    CIRCLE = 'circle'
    SQUARE = 'square'
    ROUNDED_RECT = 'rounded_rect'

class ArrowOptions:
    # type aliases
    Type = str
    Position = str

    SOLID = 'solid'
    DASHED = 'dashed'

    CENTER = 'center'
    EDGE = 'edge'
    HEAD = 'head'
    TAIL = 'tail'

    def __init__(self, arrow_type: Type, head_position: Position, tail_position: Position):
        self.arrow_type = arrow_type
        self.head_position = head_position
        self.tail_position = tail_position


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


class SceneObject:
    def export(self) -> 'json':
        return dict()


class Arrow(SceneObject):
    def __init__(self, tail_obj: BasicShape, head_obj: BasicShape, options: ArrowOptions):
        self._head_obj = head_obj
        self._tail_obj = tail_obj
        self._options = options

    # TODO
    def get_head_x(self) -> int:
        pass

    def get_head_y(self) -> int:
        pass

    def get_tail_x(self) -> int:
        pass

    def get_tail_y(self) -> int:
        pass

    def export(self) -> 'json':
        json = SceneObject.export(self)

        add_json = {
            'tail_x': self.get_tail_x(),
            'tail_y': self.get_tail_y(),
            'head_x': self.get_head_x(),
            'head_y': self.get_head_y(),
            'arrow_type': self._options.arrow_type,
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class BasicShape(SceneObject):
    SHAPE = Shape.NONE

    def __init__(self, width=None, height=None):
        SceneObject.__init__(self)

        self._width = width
        self._height = height

        # Default values
        self._header = None
        self._content = None
        self._x = None
        self._y = None

    def _calculate_edge_pos(self, angle: float) -> (float, float):
        pass
        # calculates the x and y of the edge based on the angle and the shape

    def set_width(self, width: float) -> None:
        self._width = width

    def set_height(self, height: float) -> None:
        self._height = height

    def set_size(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_header(self, header: str) -> None:
        self._header = header

    def set_content(self, content: str) -> None:
        self._content = content

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

    def get_shape(self) -> Shape.Type:
        return type(self).SHAPE

    def get_pos(self) -> (float, float):
        return (self.get_x(), self.get_y())

    def export(self) -> 'json':
        json = SceneObject.export(self)

        add_json = {
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'header': self._header,
            'content': self._content,
            'shape': self.get_shape()
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class CollectionContents:
    def __len__(self) -> int:
        pass

    def __iter__(self) -> 'iterator':
        pass

    def set_x(new_x: int):
        x_shift = new_x - self._first_element().get_x()

        for element in self.:
            shifted_x = element.get_x() + x_shift
            element.set_x(shifted_x)

    def set_y(new_y: int):
        y_shift = new_y - self._first_element().get_y()

        for element in self:
            shifted_y = element.get_y() + y_shift
            element.set_y(shifted_y)

    def _first_element(self) -> SceneObject:
        for element in self:
            return element


class Collection(BasicShape):
    SHAPE = Shape.ROUNDED_RECT

    def __init__(self):
        BasicShape.__init__(self)
        self.set_contents('')

    def get_contents(self) -> CollectionContents:
        return self._contents

    def set_contents(self, contents: CollectionContents, settings: CollectionSettings) -> None:
        self._contents = contents
        self._settings = settings    

        collection_length = len(contents)

        if collection_length == 0:
            width = settings.hmargin * 2
            height = settings.vmargin * 2
        else:
            if settings.dir == CollectionSettings.HORIZONTAL:
                width = settings.hmargin * 2 + settings.var_margin * (collection_length - 1) + Variable.SIZE * collection_length
                height = settings.vmargin * 2 + Variable.SIZE
            else:
                width = settings.hmargin * 2 + Variable.SIZE
                height = settings.vmargin * 2 + settings.var_margin * (collection_length - 1) + Variable.SIZE * collection_length   

        self.set_size(width, height)

    def set_x(self, x: float) -> None:
        BasicShape.set_x(self, x)
        self._contents.set_x(x)

    def set_y(self, y: float) -> None:
        BasicShape.set_y(self, y)
        self._contents.set_y(y)

    def __len__(self) -> int:
        return len(self._contents)

    def __iter__(self) -> 'iterator':
        return iter(self._contents)


class SectionStructure(CollectionContents):
    # TODO: add functions for creating an empty SectionStructure and modifying it like a dict of list of lists

    def __init__(self, sections: {str: [[BasicShape]]}, section_order: [str], reorderable: bool, section_reorderable: bool):
        self._sections = sections
        self._section_order = section_order
        self._reorderable = reorderable
        self._section_reorderable = section_reorderable

    def get_sections(self) -> {str: [[Variable]]}:
        return self._sections

    def get_section_order(self) -> [str]:
        return self._section_order

    def is_reorderable(self) -> bool:
        return self._reorderable

    def is_section_reorderable(self) -> bool:
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

    def __len__(self) -> int:
        def length_of_section(section: [[BasicShape]]):
            return sum(len(group) for group in section)

        return sum(length_of_section(section) for section in self._sections.values())

    def __iter__(self) -> BasicShape:
        for section in [self._sections[section] for section in self._section_order]:
            for group in section:
                for element in group:
                    yield element


class Container(BasicShape):
    H_MARGIN = 5
    V_MARGIN = 5
    SHAPE = Shape.ROUNDED_RECT

    def __init__(self):
        BasicShape.__init__(self)
        self.set_contents('')

    def get_attrs(self) -> Collection:
        return self.attrs

    def set_attrs(self, attrs: Collection):
        self._attrs = attrs
        self.set_size(Container.H_MARGIN * 2 + attrs.get_width(), Container.V_MARGIN * 2 + attrs.get_height())


class Scene:
    def __init__(self):
        self._directory: {str : SceneObject} = {}

    def gps(self) -> None:
        pass

    def export(self) -> [dict]:
        return [scene_obj.export() for scene_obj in self._directory.values()]


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
        json = {
            'scenes' : {},
            'output' : self._output
        }

        for name, scene in self._scenes.items():
            json['scenes'][name] = scene.export()

        return json
