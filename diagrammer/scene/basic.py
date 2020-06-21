from collections import OrderedDict, namedtuple
import math


class ConstructorError(Exception):
    pass


class Shape:
    Type = str # shape option type alias

    NO_SHAPE = 'no_shape'
    CIRCLE = 'circle'
    SQUARE = 'square'
    ROUNDED_RECT = 'rounded_rect'

class ArrowSettings:
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
    def construct(self, width: float, height: float, header: str, content: str):
        self._width = width
        self._height = height
        self._header = header
        self._content = content

        # explicitly create blank x and y
        self._x = None
        self._y = None

    def calculate_edge_pos(self, angle: float) -> (float, float):
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

    def set_corner_x(self, x: float) -> None:
        self.set_x(x + self._width / 2)

    def set_corner_y(self, y: float) -> None:
        self.set_y(y + self._height / 2)

    def set_corner_pos(self, x: float, y: float) -> None:
        self.set_corner_x(x)
        self.set_corner_y(y)

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

    def get_pos(self) -> (float, float):
        return (self.get_x(), self.get_y())

    def get_corner_x(self) -> float:
        return self.get_x() - self._width / 2

    def get_corner_y(self) -> float:
        return self.get_y() - self._height / 2

    def get_corner_pos(self) -> (float, float):
        return (self.get_corner_x(), self.get_corner_y())

    def get_shape(self) -> Shape.Type:
        return type(self).SHAPE

    def export(self) -> 'json':
        json = SceneObject.export(self)

        add_json = {
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'header': self._header,
            'content': self._content,
            'shape': self.SHAPE,
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class Square(BasicShape):
    SHAPE = Shape.SQUARE

    def construct(self, size: float, header: str, content: str):
        BasicShape.construct(self, size, size, header, content)
        self._size = size

    def calculate_edge_pos(self, angle: float) -> (float, float):
        standard_dangle = math.degrees(angle) % 360

        if (315 <= standard_dangle < 360) or (0 <= standard_dangle < 45):
            tri_height = math.sin(angle) * (self._width / 2) / math.sin(math.pi / 2 - angle)
            return (self._x + self._width / 2, self._y - tri_height)
        elif 45 <= standard_dangle < 135:
            tri_width = math.sin(math.pi / 2 - angle) * (self._height / 2) / math.sin(angle)
            return (self._x + tri_width, self._y - self._height / 2)
        elif 135 <= standard_dangle < 225:
            tri_height = math.sin(math.pi - angle) * (self._width / 2) / math.sin(angle - math.pi / 2)
            return (self._x - self._width / 2, self._y - tri_height)
        elif 225 <= standard_dangle < 315:
            tri_width = math.sin(3 * math.pi / 2 - angle) * (self._height / 2) / math.sin(angle - math.pi)
            return (self._x - tri_width, self._y + self._height / 2)
        else:
            raise FloatingPointError(f'BasicShape._calculate_square_edge_pos: angle {angle} is invalid')

    def get_size(self) -> float:
        return self._size


class Circle(BasicShape):
    SHAPE = Shape.CIRCLE

    def construct(self, radius: float, header: str, content: str):
        BasicShape.construct(self, radius * 2, radius * 2, header, content)
        self._radius = radius

    def calculate_edge_pos(self, angle: float) -> (float, float):
        assert self._width == self._height, f'BasicShape._calculate_circle_edge_pos: width {self._width} is not equal to height {self._height}'

        radius = self._width / 2
        return (self._x + radius * math.cos(angle), self._y - radius * math.sin(angle))

    def get_radius(self) -> float:
        return self._radius


class RoundedRect(BasicShape):
    SHAPE = Shape.ROUNDED_RECT

    def construct(self, width: float, height: float, radius: float, header: str, content: str):
        BasicShape.construct(self, width, height, header, content)
        self._radius = radius

        # precalculate variables used for calculate_edge_pos
        self._straight_width = width - radius * 2
        self._straight_height = height - radius * 2

        atan_heights = [self._straight_height / 2, height / 2, height / 2, self._straight_height / 2, -self._straight_height / 2, -height / 2, -height / 2, -self._straight_height / 2]
        atan_widths = [width / 2, self._straight_width / 2, -self._straight_width / 2, -width / 2, -width / 2, -self._straight_width / 2, self._straight_width / 2, width / 2]
        self._turning_angles = [math.atan2(atan_heights[i], atan_widths[i]) for i in range(8)]

    def calculate_edge_pos(self, angle: float) -> (float, float):
        pass


class Arrow(SceneObject):
    HEAD = 'head'
    TAIL = 'tail'

    def __init__(self, tail_obj: BasicShape, head_obj: BasicShape, settings: ArrowSettings):
        self._tail_obj = tail_obj
        self._head_obj = head_obj
        self._settings = settings

        # caching
        self._old_tail_pos = None
        self._old_head_pos = None
        self._edge_pos_cache = {Arrow.HEAD: None, Arrow.TAIL: None}

    def get_tail_pos(self) -> (float, float):
        return self._get_end_pos(Arrow.TAIL)

    def get_head_pos(self) -> (float, float):
        return self._get_end_pos(Arrow.HEAD)

    # the say_cached option is only used to test if caching actually happens
    def _get_end_pos(self, side: str, say_cached = False) -> (float, float):
        if side == Arrow.TAIL:
            edge_angle = self.get_tail_angle()
            arrow_position = self._settings.tail_position
            base_obj = self._tail_obj
        elif side == Arrow.HEAD:
            edge_angle = self.get_head_angle()
            arrow_position = self._settings.head_position
            base_obj = self._head_obj
        else:
            raise KeyError(f'Arrow._get_end_pos: side {side} is not a valid input')

        if arrow_position == ArrowSettings.CENTER:
            return base_obj.get_pos()
        elif arrow_position == ArrowSettings.EDGE:
            if self._old_tail_pos == self._tail_obj.get_pos() and self._old_head_pos == self._head_obj.get_pos():
                if say_cached:
                    return 'cached'

                return self._edge_pos_cache[side]
            else:
                self._old_tail_pos = self._tail_obj.get_pos()
                self._old_head_pos = self._head_obj.get_pos()
                self._edge_pos_cache[Arrow.TAIL] = self._tail_obj.calculate_edge_pos(self.get_tail_angle())
                self._edge_pos_cache[Arrow.HEAD] = self._head_obj.calculate_edge_pos(self.get_head_angle())
                return self._edge_pos_cache[side]

    def get_tail_angle(self) -> float:
        return math.atan2(self._tail_obj.get_y() - self._head_obj.get_y(), self._head_obj.get_x() - self._tail_obj.get_x())

    def get_head_angle(self) -> float:
        return math.atan2(self._head_obj.get_y() - self._tail_obj.get_y(), self._tail_obj.get_x() - self._head_obj.get_x())

    def export(self) -> 'json':
        json = SceneObject.export(self)

        add_json = {
            'tail_x': self.get_tail_x(),
            'tail_y': self.get_tail_y(),
            'head_x': self.get_head_x(),
            'head_y': self.get_head_y(),
            'arrow_type': self._settings.arrow_type,
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
            element.set_corner_x(self.get_corner_x() + self._settings.hmargin + i * (self._settings.cell_gap + self._settings.cell_size))

    def set_y(self, y: float) -> None:
        BasicShape.set_y(self, y)

        for element in self._contents:
            element.set_corner_y(self.get_corner_y() + self._settings.vmargin)

    def __len__(self) -> int:
        return len(self._contents)

    def __iter__(self) -> 'iterator':
        return iter(self._contents)


class Container(BasicShape):
    H_MARGIN = 5
    V_MARGIN = 5
    SHAPE = Shape.ROUNDED_RECT

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
    def __init__(self, scenes: OrderedDict, output: str, error: bool):
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
            'scenes' : {},
            'output' : self._output,
            'error' : self._error,
        }

        for name, scene in self._scenes.items():
            json['scenes'][name] = scene.export()

        return json
