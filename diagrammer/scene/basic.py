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

    def svg(self) -> str:
        pass


class BasicShape(SceneObject):
    HEADER_MARGIN = 5

    def construct(self, width: float, height: float, header: str, content: str):
        self._width = width
        self._height = height
        self._header = header
        self._content = content

        # explicitly create blank x and y
        self._x = None
        self._y = None
        self._in_degree = 0

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

    def inc_in_degree(self):
        self._in_degree += 1

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

    def get_in_degree(self) -> int:
        return self._in_degree

    def header_x(self) -> float:
        return self._x

    def header_y(self) -> float:
        return self.get_corner_y() - BasicShape.HEADER_MARGIN

    def header_pos(self) -> (float, float):
        return (self.header_x(), self.header_y())

    def content_x(self) -> float:
        return self._x

    def content_y(self) -> float:
        return self._y

    def content_pos(self) -> (float, float):
        return (self.content_x(), self.content_y())

    def export(self) -> 'json':
        json = SceneObject.export(self)

        add_json = {
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'header': {
                'x' : self.header_x(),
                'y' : self.header_y(),
                'text' : self._header
            },
            'content': {
                'x' : self.content_x(),
                'y' : self.content_y(),
                'text' : self._content
            },
            'shape': self.get_shape(),
        }

        for key, val in add_json.items():
            json[key] = val

        return json

    def svg(self) -> str:
        pass


class Square(BasicShape):
    SHAPE = Shape.SQUARE

    def construct(self, size: float, header: str, content: str):
        BasicShape.construct(self, size, size, header, content)

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

    def svg(self) -> str:
        return f'''
        <g>
            <text class="gold-text" text-anchor="middle" x="{self.header_x()}" y="{self.header_y()}">{self.get_header()}</text>
            <rect class="var" x="{self.get_corner_x()}" y="{self.get_corner_y()}" width="{self.get_width()}" height="{self.get_height()}"></rect>
            <text class="gold-text" text-anchor="middle" alignment-baseline="central" x="{self.content_x()}" y="{self.content_y()}">{self.get_content()}</text>
        </g>
        '''


class Circle(BasicShape):
    SHAPE = Shape.CIRCLE

    def construct(self, radius: float, header: str, content: str):
        BasicShape.construct(self, radius * 2, radius * 2, header, content)

    def calculate_edge_pos(self, angle: float) -> (float, float):
        return (self._x + self._width / 2 * math.cos(angle), self._y - self._height / 2 * math.sin(angle))

    def svg(self) -> str:
        return f'''
        <g>
            <text class="gold-text" text-anchor="middle" x="{self.header_x()}" y="{self.header_y()}">{self.get_header()}</text>
            <ellipse class="var" cx="{self.get_x()}" cy="{self.get_y()}" rx="{self.get_width() / 2}" ry="{self.get_height() / 2}"></ellipse>
            <text class="gold-text" text-anchor="middle" alignment-baseline="central" x="{self.content_x()}" y="{self.content_y()}">{self.get_content()}</text>
        </g>
        '''


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

        if (self._transition_dangles[7] == 0):
            self._transition_dangles[7] = 360

    def calculate_edge_pos(self, angle: float) -> (float, float):
        standard_dangle = math.degrees(angle) % 360

        # we need to check that it's not equal to 0 because if it is 0 then every single angle check ends here since 0 < 360, but conceptually 0 is supposed to be 360
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
            raise ValueError(f'RoundedRect._calculate_square_edge_pos: standard_dangle {standard_dangle} is invalid')

    def export(self) -> 'json':
        json = BasicShape.export(self)

        add_json = {
            'corner_radius': self._corner_radius
        }

        for key, val in add_json.items():
            json[key] = val

        return json

    def svg(self) -> str:
        return f'''
        <g>
            <text class="gold-text" text-anchor="middle" x="{self.header_x()}" y="{self.header_y()}">{self.get_header()}</text>
            <rect class="var" x="{self.get_corner_x()}" y="{self.get_corner_y()}" width="{self.get_width()}" height="{self.get_height()}" rx="{self._corner_radius}" ry="{self._corner_radius}"></rect>
            <text class="gold-text" text-anchor="middle" alignment-baseline="central" x="{self.content_x()}" y="{self.content_y()}">{self.get_content()}</text>
        </g>
        '''


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

    def svg(self) -> str:
        return f'''
        <g>
            <marker id="markerArrow" markerWidth="13" markerHeight="13" refX="10" refY="6" orient="auto">
                <path class="ref-arrow-head" d="M2,2 L2,11 L10,6 L2,2"></path>
            </marker>

            <line class="ref" x1="{self.get_tail_x()}" y1="{self.get_tail_y()}" x2="{self.get_head_x()}" y2="{self.get_head_y()}" marker-end="url(#markerArrow)"></line>
        </g>
        '''


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
        self._coll.set_x(x)

    def set_y(self, y: float) -> None:
        RoundedRect.set_y(self, y)
        self._coll.set_y(y)

    def get_coll(self) -> Collection:
        return self._coll


class Scene:
    def __init__(self):
        self._directory: {str : SceneObject} = {}

        self._width = 0
        self._height = 0

    def gps(self) -> None:
        pass

    def export(self) -> dict:
        return {
            'width' : self._width,
            'height' : self._height,
            'contents' : [scene_obj.export() for scene_obj in self._directory.values()],
        }

    def svg(self) -> str:
        indent = '\n\t'

        return f'''
        <svg class="scene{'' if self._directory != {} else ' empty'}" width="{self._width if self._width > 0 else 500}" height="{self._height if self._height > 0 else 600}">
            {indent.join(scene_obj.svg() for scene_obj in self._directory.values())}
        </svg>
        '''


class Snapshot:
    def __init__(self, scenes: dict, output: str, error: str):
        self._scenes = scenes
        self._output = output
        self._error = error

    def get_scenes(self) -> dict:
        return self._scenes

    def get_scene(self, name: str) -> Scene:
        return self._scenes[name]

    def get_output(self) -> str:
        return self._output

    def export(self, scene_format='json'):
        if scene_format == 'json':
            scene_data = {name : scene.export() for name, scene in self._scenes.items()}
        elif scene_format == 'svg':
            scene_data = {name : scene.svg() for name, scene in self._scenes.items()}
        else:
            scene_data = {} # eventually throw error but that's not a priority

        json = {
            'scenes' : scene_data,
            'output' : self._output,
            'error' : self._error,
        }

        return json
