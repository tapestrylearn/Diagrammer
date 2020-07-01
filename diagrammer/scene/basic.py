from collections import OrderedDict, namedtuple
import math


class ConstructorError(Exception):
    pass


class Shape:
    Type = str # shape option type alias

    NO_SHAPE = 'no_shape'
    CIRCLE = 'circle'
    BOX = 'box'
    ROUNDED_RECT = 'rounded_rect'

class ArrowOptions:
    # type aliases
    Type = str
    Position = str

    SOLID = 'solid'
    DASHED = 'dashed'

    CENTER = 'center'
    EDGE = 'edge'

    def __init__(self, arrow_type: Type, head_position: Position, tail_position: Position):
        self.arrow_type = arrow_type
        self.head_position = head_position
        self.tail_position = tail_position


class CollectionSettings:
    Direction = int

    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, hmargin: float, vmargin: float, cell_gap: float, dir: Direction, cell_size: float):
        self.hmargin = hmargin
        self.vmargin = vmargin
        self.cell_gap = cell_gap
        self.dir = dir
        self.cell_size = cell_size


class ReorderException(Exception):
    pass


class SceneObject:
    def export(self) -> 'json':
        return dict()


class BasicShape(SceneObject):
    SHAPE = Shape.NO_SHAPE

    def __init__(self):
        SceneObject.__init__(self)

    def construct(self, width: float, height: float, header: str, content: str):
        self._width = width
        self._height = height
        self._header = header
        self._content = content

        # explicitly create blank width and height
        self._x = None
        self._y = None

    def calculate_edge_pos(self, angle: float) -> (float, float):
        if self.get_shape() == Shape.NO_SHAPE:
            return (self._x, self._y)
        elif self.get_shape() == Shape.CIRCLE:
            return (self._x + math.cos(angle), self._y + math.sin(angle))
        else:
            return (self._x, self._y)

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

    def is_positioned(self) -> bool:
        return self._x != None and self._y != None

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
            'shape': self.get_shape(),
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class Arrow(SceneObject):
    def __init__(self, tail_obj: BasicShape, head_obj: BasicShape, options: ArrowOptions):
        self._head_obj = head_obj
        self._tail_obj = tail_obj
        self._options = options

    def get_head_x(self) -> float:
        if self._options.head_position == ArrowOptions.CENTER:
            return self._head_obj.get_x() + self._head_obj.get_width() / 2
        elif self._options.head_position == ArrowOptions.EDGE:
            angle = math.atan2(self._tail_obj.get_y() - self._head_obj.get_y(), self._tail_obj.get_x() - self._head_obj.get_x())
            return self._head_obj.calculate_edge_pos(angle)[0]

    def get_head_y(self) -> float:
        if self._options.head_position == ArrowOptions.CENTER:
            return self._head_obj.get_y() + self._head_obj.get_height() / 2
        elif self._options.head_position == ArrowOptions.EDGE:
            angle = math.atan2(self._tail_obj.get_y() - self._head_obj.get_y(), self._tail_obj.get_x() - self._head_obj.get_x())
            return self._head_obj.calculate_edge_pos(angle)[1]

    def get_tail_x(self) -> float:
        if self._options.tail_position == ArrowOptions.CENTER:
            return self._tail_obj.get_x() + self._tail_obj.get_width() / 2
        elif self._options.tail_position == ArrowOptions.EDGE:
            angle = math.atan2(self._head_obj.get_y() - self._tail_obj.get_y(), self._head_obj.get_x() - self._tail_obj.get_x())
            return self._tail_obj.calculate_edge_pos(angle)[0]

    def get_tail_y(self) -> float:
        if self._options.tail_position == ArrowOptions.CENTER:
            return self._tail_obj.get_y() + self._tail_obj.get_height() / 2
        elif self._options.tail_position == ArrowOptions.EDGE:
            angle = math.atan2(self._head_obj.get_y() - self._tail_obj.get_y(), self._head_obj.get_x() - self._tail_obj.get_x())
            return self._tail_obj.calculate_edge_pos(angle)[1]

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


# we should make this just an iter
class CollectionContents:
    def __len__(self) -> int:
        pass

    def __iter__(self) -> 'iterator':
        pass


class Collection(BasicShape):
    SHAPE = Shape.ROUNDED_RECT

    def __init__(self):
        BasicShape.__init__(self)

    def get_contents(self) -> CollectionContents:
        return self._contents

    def construct(self, header: str, contents: CollectionContents, settings: CollectionSettings):
        self._contents = contents
        self._settings = settings

        collection_length = 0 if self._contents == None else len(self._contents)

        if collection_length == 0:
            width = self._settings.hmargin * 2
            height = self._settings.vmargin * 2
        else:
            if settings.dir == CollectionSettings.HORIZONTAL:
                width = self._settings.hmargin * 2 + self._settings.cell_gap * (collection_length - 1) + self._settings.cell_size * collection_length
                height = self._settings.vmargin * 2 + self._settings.cell_size
            else:
                width = self._settings.hmargin * 2 + self._settings.cell_size
                height = self._settings.vmargin * 2 + self._settings.cell_gap * (collection_length - 1) + self._settings.cell_size * collection_length

        BasicShape.construct(self, width, height, header, '')

    def set_x(self, x: float) -> None:
        BasicShape.set_x(self, x)

        for i, element in enumerate(self._contents):
            element.set_x(x + self._settings.hmargin + i * (self._settings.cell_gap + self._settings.cell_size))

    def set_y(self, y: float) -> None:
        BasicShape.set_y(self, y)

        for element in self._contents:
            element.set_y(y + self._settings.vmargin)

    def __len__(self) -> int:
        return len(self._contents)

    def __iter__(self) -> 'iterator':
        return iter(self._contents)


class Container(BasicShape):
    H_MARGIN = 5
    V_MARGIN = 5
    SHAPE = Shape.ROUNDED_RECT

    def __init__(self):
        BasicShape.__init__(self)

    def construct(self, header: str, coll: Collection, hmargin: float, vmargin: float):
        BasicShape.construct(self, hmargin * 2 + coll.get_width(), vmargin * 2 + coll.get_height(), header, '')
        self._coll = coll
        self._hmargin = hmargin
        self._vmargin = vmargin

    def set_x(self, x: float) -> None:
        BasicShape.set_x(self, x)
        self._coll.set_x(x + self._hmargin)

    def set_y(self, y: float) -> None:
        BasicShape.set_y(self, y)
        self._coll.set_y(y + self._vmargin)

    def get_coll(self) -> Collection:
        return self._coll


class Scene:
    def __init__(self):
        self._directory: {str : SceneObject} = {}

    def gps(self) -> None:
        pass

    def export(self) -> [dict]:
        return [scene_obj.export() for scene_obj in self._directory.values()]


class Snapshot:
    def __init__(self, scenes: OrderedDict, output: str, error: str):
        self._scenes = scenes
        self._output = output
        self._error = error

    def get_scenes(self) -> OrderedDict:
        return self._scenes

    def get_scene(self, name: str) -> Scene:
        return self._scenes[name]

    def get_output(self) -> str:
        return self._output

    def export(self):
        json = {
            'scenes' : {name : scene.export() for name, scene in self._scenes.items()},
            'output' : self._output,
            'error' : self._error,
        }

        return json
