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

    def __init__(self, hmargin: float, vmargin: float, cell_gap: float, dir: Direction, cell_size: float, corner_radius: float):
        self.hmargin = hmargin
        self.vmargin = vmargin
        self.cell_gap = cell_gap
        self.dir = dir
        self.cell_size = cell_size
        self.corner_radius = corner_radius


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

    # only override set_x and set_y, nothing else
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

    def collides(self, other: 'BasicShape'):
        x_diff = other._x - self._y
        y_diff = other._y - self._y

        if x_diff == 0:
            x_collides = True
        elif x_diff > 0:
            x_collides = other._x - other._width / 2 < self._x + self._width / 2
        else:
            x_collides = other._x + other._width / 2 > self._x - self._width / 2

        if y_diff == 0:
            y_collides = True
        elif y_diff > 0:
            y_collides = other._y - other._height / 2 < self._y + self._height / 2
        else:
            y_collides = other._y + other._height / 2 > self._y - self._height / 2

        return x_collides and y_collides


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
            raise FloatingPointError(f'Square._calculate_square_edge_pos: angle {angle} is invalid')

    def get_size(self) -> float:
        return self._size

    def export(self) -> 'json':
        json = BasicShape.export(self)

        add_json = {
            'size': self._size,
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class Circle(BasicShape):
    SHAPE = Shape.CIRCLE

    def construct(self, radius: float, header: str, content: str):
        BasicShape.construct(self, radius * 2, radius * 2, header, content)
        self._radius = radius

    def calculate_edge_pos(self, angle: float) -> (float, float):
        return (self._x + self._radius * math.cos(angle), self._y - self._radius * math.sin(angle))

    def get_radius(self) -> float:
        return self._radius

    def export(self) -> 'json':
        json = BasicShape.export(self)

        add_json = {
            'radius': self._radius
        }

        for key, val in add_json.items():
            json[key] = val

        return json


class RoundedRect(BasicShape):
    SHAPE = Shape.ROUNDED_RECT

    def construct(self, width: float, height: float, corner_radius: float, header: str, content: str):
        BasicShape.construct(self, width, height, header, content)
        self._corner_radius = corner_radius

        # precalculate variables used for calculate_edge_pos
        self._straight_width = width - corner_radius * 2
        self._straight_height = height - corner_radius * 2

        atan_heights = [self._straight_height / 2, height / 2, height / 2, self._straight_height / 2, -self._straight_height / 2, -height / 2, -height / 2, -self._straight_height / 2]
        atan_widths = [width / 2, self._straight_width / 2, -self._straight_width / 2, -width / 2, -width / 2, -self._straight_width / 2, self._straight_width / 2, width / 2]
        self._transition_dangles = [math.degrees(math.atan2(atan_heights[i], atan_widths[i])) % 360 for i in range(8)]

    def calculate_edge_pos(self, angle: float) -> (float, float):
        standard_dangle = math.degrees(angle) % 360

        if (self._transition_dangles[7] <= standard_dangle < 360) or (0 <= standard_dangle < self._transition_dangles[0]):
            tri_height = math.sin(angle) * (self._width / 2) / math.sin(math.pi / 2 - angle)
            return (self._x + self._width / 2, self._y - tri_height)
        elif self._transition_dangles[0] <= standard_dangle < self._transition_dangles[1]:
            circle_center_x = self._x + self._straight_width / 2
            circle_center_y = self._y - self._straight_height / 2
            return (circle_center_x + self._corner_radius * math.cos(angle), circle_center_y - self._corner_radius * math.sin(angle))
        elif self._transition_dangles[1] <= standard_dangle < self._transition_dangles[2]:
            tri_width = math.sin(math.pi / 2 - angle) * (self._height / 2) / math.sin(angle)
            return (self._x + tri_width, self._y - self._height / 2)
        elif self._transition_dangles[2] <= standard_dangle < self._transition_dangles[3]:
            circle_center_x = self._x - self._straight_width / 2
            circle_center_y = self._y - self._straight_height / 2
            return (circle_center_x + self._corner_radius * math.cos(angle), circle_center_y - self._corner_radius * math.sin(angle))
        elif self._transition_dangles[3] <= standard_dangle < self._transition_dangles[4]:
            tri_height = math.sin(math.pi - angle) * (self._width / 2) / math.sin(angle - math.pi / 2)
            return (self._x - self._width / 2, self._y - tri_height)
        elif self._transition_dangles[4] <= standard_dangle < self._transition_dangles[5]:
            circle_center_x = self._x - self._straight_width / 2
            circle_center_y = self._y + self._straight_height / 2
            return (circle_center_x + self._corner_radius * math.cos(angle), circle_center_y - self._corner_radius * math.sin(angle))
        elif self._transition_dangles[5] <= standard_dangle < self._transition_dangles[6]:
            tri_width = math.sin(3 * math.pi / 2 - angle) * (self._height / 2) / math.sin(angle - math.pi)
            return (self._x - tri_width, self._y + self._height / 2)
        elif self._transition_dangles[6] <= standard_dangle < self._transition_dangles[7]:
            circle_center_x = self._x + self._straight_width / 2
            circle_center_y = self._y + self._straight_height / 2
            return (circle_center_x + self._corner_radius * math.cos(angle), circle_center_y - self._corner_radius * math.sin(angle))
        else:
            raise ValueError(f'RoundedRect._calculate_square_edge_pos: angle {angle} is invalid')

    def export(self) -> 'json':
        json = BasicShape.export(self)

        add_json = {
            'corner_radius': self._corner_radius
        }

        for key, val in add_json.items():
            json[key] = val

        return json


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

    def get_center_tail_pos(self) -> (float, float):
        return self._tail_obj.get_pos()

    def get_center_head_pos(self) -> (float, float):
        return self._head_obj.get_pos()

    def get_center_tail_x(self) -> float:
        return self.get_center_tail_pos()[0]

    def get_center_tail_y(self) -> float:
        return self.get_center_tail_pos()[1]

    def get_center_head_x(self) -> float:
        return self.get_center_head_pos()[0]

    def get_center_head_y(self) -> float:
        return self.get_center_head_pos()[1]

    def get_tail_pos(self) -> (float, float):
        return self._get_end_pos(Arrow.TAIL)

    def get_head_pos(self) -> (float, float):
        return self._get_end_pos(Arrow.HEAD)

    def get_tail_x(self) -> float:
        return self.get_tail_pos()[0]

    def get_tail_y(self) -> float:
        return self.get_tail_pos()[1]

    def get_head_x(self) -> float:
        return self.get_head_pos()[0]

    def get_head_y(self) -> float:
        return self.get_head_pos()[1]

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


    # intersection function from: https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    def _intersects(self, p2: (float, float), q2: (float, float)):
        def orientation(p: (float, float), q: (float, float), r: (float, float)):
            val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))

            if (val > 0):
                # Clockwise orientation
                return 1
            elif (val < 0):
                # Counterclockwise orientation
                return 2
            else:
                # Colinear orientation
                return 0

        def on_segment(p, q, r):
            if ((q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and
                   (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
                return True
            return False

        p1 = self.get_center_tail_pos()
        q1 = self.get_center_head_pos()

        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)

        # General case
        if ((o1 != o2) and (o3 != o4)):
            return True

        # Special Cases

        # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
        if ((o1 == 0) and on_segment(p1, p2, q1)):
            return True

        # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
        if ((o2 == 0) and on_segment(p1, q2, q1)):
            return True

        # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
        if ((o3 == 0) and on_segment(p2, p1, q2)):
            return True

        # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
        if ((o4 == 0) and on_segment(p2, q1, q2)):
            return True

        # If none of the cases
        return False

    def intersects_arrow(self, arrow: 'Arrow') -> bool:
        p2 = arrow.get_center_tail_pos()
        q2 = arrow.get_center_head_pos()
        return self._intersects(p2, q2)

    def intersects_shape(self, shape: BasicShape):
        top_left = shape.get_corner_pos()
        top_right = (shape.get_corner_x() + shape.get_width(), shape.get_corner_y())
        bot_left = (shape.get_corner_x(), shape.get_corner_y() + shape.get_height())
        bot_right = (shape.get_corner_x() + shape.get_width(), shape.get_corner_y() + shape.get_height())

        intersects_top = self._intersects(top_left, top_right)
        intersects_right = self._intersects(top_right, bot_right)
        intersects_bot = self._intersects(bot_left, bot_right)
        intersects_left = self._intersects(top_left, bot_left)
        inside_x = shape.get_corner_x() < min(self.get_center_head_x(), self.get_center_tail_x()) and max(self.get_center_head_x(), self.get_center_tail_x()) < shape.get_corner_x() + shape.get_width()
        inside_y = shape.get_corner_y() < min(self.get_center_head_y(), self.get_center_tail_y()) and max(self.get_center_head_y(), self.get_center_tail_y()) < shape.get_corner_y() + shape.get_height()
        inside_x = False

        return intersects_top or intersects_right or intersects_bot or intersects_left or (inside_x and inside_y)


# we should make this just an iter
class CollectionContents:
    def __len__(self) -> int:
        pass

    def __iter__(self) -> 'iterator':
        pass


class Collection(RoundedRect):
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
            elif settings.dir == CollectionSettings.VERTICAL:
                width = self._settings.hmargin * 2 + self._settings.cell_size
                height = self._settings.vmargin * 2 + self._settings.cell_gap * (collection_length - 1) + self._settings.cell_size * collection_length
            else:
                raise KeyError(f'Collection.construct: settings.dir {settings.dir} is not HORIZONTAL or VERTICAL')

        RoundedRect.construct(self, width, height, settings.corner_radius, header, '')

    def set_x(self, x: float) -> None:
        RoundedRect.set_x(self, x)

        for (i, element) in enumerate(self._contents):
            if self._settings.dir == CollectionSettings.HORIZONTAL:
                element.set_corner_x(self.get_corner_x() + self._settings.hmargin + i * (self._settings.cell_gap + self._settings.cell_size))
            elif self._settings.dir == CollectionSettings.VERTICAL:
                element.set_corner_x(self.get_corner_x() + self._settings.hmargin)

    def set_y(self, y: float) -> None:
        RoundedRect.set_y(self, y)

        for (i, element) in enumerate(self._contents):
            if self._settings.dir == CollectionSettings.HORIZONTAL:
                element.set_corner_y(self.get_corner_y() + self._settings.vmargin)
            elif self._settings.dir == CollectionSettings.VERTICAL:
                element.set_corner_y(self.get_corner_y() + self._settings.vmargin + i * (self._settings.cell_gap + self._settings.cell_size))

    def get_contents(self) -> CollectionContents:
        return self._contents

    def __len__(self) -> int:
        return len(self._contents)

    def __iter__(self) -> 'iterator':
        return iter(self._contents)


class Container(RoundedRect):
    H_MARGIN = 5
    V_MARGIN = 5

    def construct(self, header: str, coll: Collection, hmargin: float, vmargin: float, corner_radius: float):
        RoundedRect.construct(self, hmargin * 2 + coll.get_width(), vmargin * 2 + coll.get_height(), corner_radius, header, '')
        self._coll = coll
        self._hmargin = hmargin
        self._vmargin = vmargin

    def set_x(self, x: float) -> None:
        RoundedRect.set_x(self, x)
        self._coll.set_x(x + self._hmargin)

    def set_y(self, y: float) -> None:
        RoundedRect.set_y(self, y)
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
