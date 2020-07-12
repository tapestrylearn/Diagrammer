from . import scene, local_visualizer
import random
import math


# NOTE: GPS can access internal vars of PyScene since it's pretty much an internal class, it's just in its own module because there's so much code

class GPS:
    CELL_SIZE = 100
    CELL_AMOUNT = 10
    MARGIN = CELL_SIZE / 2

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
        self._variables = [val for val in self._positionable_objects if type(val) == scene.PyVariable]
        self._rvalues_connected_to_variables = {var.get_head_obj() for var in self._variables}
        self._cell_available = [[True for _ in range(GPS.CELL_AMOUNT)] for _ in range(GPS.CELL_AMOUNT)]

        for ref in self._references:
            ref.get_head_obj().inc_in_degree()

    @staticmethod
    def cell_to_pos(x_cell: int, y_cell: int) -> (float, float):
        return (GPS.MARGIN + x_cell * GPS.CELL_SIZE, GPS.MARGIN + y_cell * GPS.CELL_SIZE)

    @staticmethod
    def cell_to_coll_corner_pos(x_cell: int, y_cell: int, margin: int) -> (float, float):
        return (GPS.MARGIN + x_cell * GPS.CELL_SIZE + (GPS.CELL_SIZE / 2 - scene.PyVariable.SIZE / 2 - margin), GPS.MARGIN + y_cell * GPS.CELL_SIZE + (GPS.CELL_SIZE / 2 - scene.PyVariable.SIZE / 2 - margin))

    @staticmethod
    def cell_to_center_pos(x_cell: int, y_cell: int) -> (float, float):
        return (GPS.MARGIN + x_cell * GPS.CELL_SIZE + GPS.CELL_SIZE / 2, GPS.MARGIN + y_cell * GPS.CELL_SIZE + GPS.CELL_SIZE / 2)

    @staticmethod
    def xory_pos_to_cell(xory: float) -> int:
        return math.floor((xory - GPS.MARGIN) / GPS.CELL_SIZE)

    def run(self) -> None:
        # first make everything disappear (for testing purposes)
        for scene_obj in self._positionable_objects:
            scene_obj.set_corner_pos(600, 600)

        # position edge basic values with in-degree 1
        val_start_cell = 1

        def get_next_variable_connected_val_cell() -> (float, float):
            yield (val_start_cell, val_start_cell)

            for i in range(val_start_cell + 1, GPS.CELL_AMOUNT):
                yield (i, val_start_cell)
                yield (val_start_cell, i)

        next_cell_iterator = get_next_variable_connected_val_cell()

        for rval in self._rvalues_connected_to_variables:
            if rval.get_in_degree() == 1 and type(rval) == scene.PyBasicValue:
                cell = next_cell_iterator.__next__()
                rval.set_pos(*GPS.cell_to_center_pos(*cell))
                self._cell_available[cell[1]][cell[0]] = False

        # position edge collections
        for rval in self._rvalues_connected_to_variables:
            if type(rval) == scene.PySimpleCollection:
                coll_cell_width = len(rval.get_contents())
                coll_row = val_start_cell

                while True:
                    while not self._cell_available[coll_row][val_start_cell + coll_cell_width - 1]:
                        coll_row += 1

                    if all([self._cell_available[coll_row][col] for col in range(val_start_cell, val_start_cell + coll_cell_width)]):
                        break
                    else:
                        coll_row += 1

                rval.set_corner_pos(*GPS.cell_to_coll_corner_pos(val_start_cell, coll_row, scene.PySimpleCollection.ORDERED_COLLECTION_SETTINGS.hmargin))

                for col in range(val_start_cell, val_start_cell + coll_cell_width):
                    self._cell_available[coll_row][col] = False

                # TODO: currently, I'm assuming the collection is ordered
                # position edge basic vals with in-degree 1
                positioned_in1_val = False

                for inner_var in rval.get_contents():
                    inner_val = inner_var.get_head_obj()

                    if type(inner_val) == scene.PyBasicValue and inner_val.get_in_degree() == 1:
                        inner_val_x = inner_var.get_x()
                        inner_val_y = inner_var.get_y() + GPS.CELL_SIZE
                        inner_val.set_pos(inner_val_x, inner_val_y)
                        self._cell_available[GPS.xory_pos_to_cell(inner_val_y)][GPS.xory_pos_to_cell(inner_val_x)] = False
                        positioned_in1_val = True

                cell_y_offset = 2 if positioned_in1_val else 1

                # position edge basic vals with in-degree 2
                for inner_var in reversed(rval.get_contents()):
                    inner_val = inner_var.get_head_obj()

                    if type(inner_val) == scene.PyBasicValue and inner_val.get_in_degree() == 2 and inner_val in self._rvalues_connected_to_variables:
                        inner_val_x = inner_var.get_x()
                        inner_val_y = inner_var.get_y() + GPS.CELL_SIZE * cell_y_offset
                        inner_val.set_pos(inner_val_x, inner_val_y)
                        self._cell_available[GPS.xory_pos_to_cell(inner_val_y)][GPS.xory_pos_to_cell(inner_val_x)] = False
                        cell_y_offset += 1

        # greedy position edge vars
        def get_next_variable_cell() -> (float, float):
            if self._cell_available[0][0]:
                yield (0, 0)

            for i in range(1, GPS.CELL_AMOUNT):
                if self._cell_available[0][i]:
                    yield (i, 0)

                if self._cell_available[i][0]:
                    yield (0, i)

        # TODO: make this more efficient by just going left/up from the variable's value
        for var in self._variables:
            shortest_len = GPS.CELL_AMOUNT * GPS.CELL_SIZE * 2 # the longest possible length is GPS.CELL_AMOUNT * GPS.CELL_SIZE * math.sqrt(2)
            best_cell = None

            for var_cell in get_next_variable_cell():
                var.set_pos(*GPS.cell_to_center_pos(*var_cell))
                ref_len = var.get_ref().length()

                if ref_len < shortest_len:
                    shortest_len = ref_len
                    best_cell = var_cell

            if best_cell == None:
                raise RuntimeError('GPS.run.get_next_variable_pos: best_pos is None meaning all variable cells are full')

            var.set_pos(*GPS.cell_to_center_pos(*best_cell))
            self._cell_available[best_cell[1]][best_cell[0]] = False


        local_visualizer.generate_single_png(self._scne.export(), f'{self._scene_name}/', f'sol', f'{self._scene_name}')
