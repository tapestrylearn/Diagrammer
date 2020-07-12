from . import scene, local_visualizer
import random
import math


# NOTE: GPS can access internal vars of PyScene since it's pretty much an internal class, it's just in its own module because there's so much code

# first grid is for shapes, expand first grid into second grid (more detailed and gaps left) to position circuits

class GPS:
    CELL_SIZE = scene.PySimpleCollection.ORDERED_COLLECTION_SETTINGS.hmargin * 2 + scene.PyVariable.SIZE
    CELL_AMOUNT = 10
    MAX_BATTERY_COL = CELL_AMOUNT
    COLLECTION_GAP_BORDER = 1 # the amount of cells to leave blank around collections
    VARIABLE_COLUMN_WIDTH = 1

    def __init__(self, scne: scene.PyScene, scene_name: str):
        self._scne = scne
        self._scene_name = scene_name

        # cache useful groups in scne
        non_positionable_objects = set()

        for val in scne._directory.values():
            if type(val) == scene.PySimpleCollection or type(val) == scene.PyNamespaceCollection:
                for var in val:
                    non_positionable_objects.add(var)
            elif type(val) == scene.PyNamespace:
                non_positionable_objects.add(val.get_coll())

        self._positionable_objects = [val for val in scne._directory.values() if type(val) != scene.PyReference and val not in non_positionable_objects]
        self._positionable_rvalues = [val for val in self._positionable_objects if type(val) != scene.PyVariable]
        self._references = [val for val in scne._directory.values() if type(val) == scene.PyReference]
        self._edge_variables = [val for val in self._positionable_objects if type(val) == scene.PyVariable]
        self._rvalues_connected_to_variables = {var.get_head_obj() for var in self._edge_variables}

        for ref in self._references:
            ref.get_head_obj().inc_in_degree()

        self._cell_available = [[True] * GPS.CELL_AMOUNT] * GPS.CELL_AMOUNT
        self._collection_front = [GPS.VARIABLE_COLUMN_WIDTH] * GPS.CELL_AMOUNT # no border in initial front because you couldn't put a val in that space anyways
        self._battery_cell_height = 0

    def position_collection_layer(self, current_base_vars: [scene.PyVariable], is_edge_layer = False):
        if len(current_base_vars) == 0:
            return

        next_base_vars = []
        current_row = self._battery_cell_height + GPS.COLLECTION_GAP_BORDER

        for var in current_base_vars:
            val = var.get_head_obj()

            if not val.is_positioned() and type(val) is scene.PySimpleCollection:
                # positioning
                cell_width = GPS.size_to_cell(val.get_width())
                corner_col = self._collection_front[current_row]
                val.set_corner_pos(*GPS.cell_to_coll_corner_pos(corner_col, current_row, scene.PySimpleCollection.ORDERED_COLLECTION_SETTINGS.hmargin))

                # position edge var if this is an edge layer call
                if is_edge_layer:
                    var.set_pos(*GPS.cell_to_center_pos(0, current_row))

                for col in range(corner_col, corner_col + cell_width):
                    self._cell_available[current_row][col] = False

                # changing variables for the future
                next_base_vars.extend([var for var in val.get_contents()])
                self._collection_front[current_row] += cell_width + GPS.COLLECTION_GAP_BORDER
                current_row += 1 + GPS.COLLECTION_GAP_BORDER

        self.position_collection_layer(next_base_vars)

    def run(self) -> None:
        # create battery
        battery_col = 0
        battery_row = 0

        for var in self._edge_variables:
            val = var.get_head_obj()

            if type(val) == scene.PyBasicValue and val.get_in_degree() == 1:
                if self._battery_cell_height == 0: # this triggers the first time you enter the if
                    self._battery_cell_height = 2

                var.set_pos(*GPS.cell_to_center_pos(battery_col, battery_row))
                val.set_pos(*GPS.cell_to_center_pos(battery_col, battery_row + 1))
                battery_col += 1

                if battery_col >= GPS.MAX_BATTERY_COL:
                    battery_col = 0
                    battery_row += 2
                    self._battery_cell_height += 2

        # position collections layer by layer
        self.position_collection_layer(self._edge_variables, is_edge_layer = True)

        # position values

        # put everything else in the corner
        for scene_obj in self._positionable_objects:
            if not scene_obj.is_positioned():
                scene_obj.set_corner_pos(600, 600)

        local_visualizer.generate_single_png(self._scne.export(), f'{self._scene_name}/', f'sol', f'{self._scene_name}')

    @staticmethod
    def cell_to_pos(x_cell: int, y_cell: int) -> (float, float):
        return (x_cell * GPS.CELL_SIZE, y_cell * GPS.CELL_SIZE)

    @staticmethod
    def cell_to_coll_corner_pos(x_cell: int, y_cell: int, margin: int) -> (float, float):
        return (x_cell * GPS.CELL_SIZE + (GPS.CELL_SIZE / 2 - scene.PyVariable.SIZE / 2 - margin), y_cell * GPS.CELL_SIZE + (GPS.CELL_SIZE / 2 - scene.PyVariable.SIZE / 2 - margin))

    @staticmethod
    def cell_to_center_pos(x_cell: int, y_cell: int) -> (float, float):
        return (x_cell * GPS.CELL_SIZE + GPS.CELL_SIZE / 2, y_cell * GPS.CELL_SIZE + GPS.CELL_SIZE / 2)

    @staticmethod
    def pos_to_cell(pos: float) -> int:
        return math.floor(pos / GPS.CELL_SIZE)

    @staticmethod
    def size_to_cell(size: float) -> int:
        return math.ceil(size / GPS.CELL_SIZE)
