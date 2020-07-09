from . import scene, local_visualizer
import random


# NOTE: GPS can access internal vars of PyScene since it's pretty much an internal class, it's just in its own module because there's so much code

# MAIN ALGORITHM
# strategies
#   * position values first variables later
#   * position values that have variables pointing to them on the edge
#   * position values in order of highest collection var in-degree
class GPS:
    CELL_SIZE = 80
    CELL_AMOUNT = 8
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

    @staticmethod
    def cell_to_pos(x_cell: int, y_cell: int) -> (float, float):
        return (GPS.MARGIN + x_cell * GPS.CELL_SIZE, GPS.MARGIN + y_cell * GPS.CELL_SIZE)

    def run(self) -> None:
        # first make everything disappear (for testing purposes)
        for scene_obj in self._positionable_objects:
            scene_obj.set_corner_pos(600, 600)

        # position edge rvals
        def get_next_variable_connected_val_pos() -> (float, float):
            startCell = 1

            yield GPS.cell_to_pos(startCell, startCell)

            for i in range(startCell + 1, GPS.CELL_AMOUNT):
                yield GPS.cell_to_pos(i, startCell)
                yield GPS.cell_to_pos(startCell, i)

        next_pos_iterator = get_next_variable_connected_val_pos()

        for rval in self._rvalues_connected_to_variables:
            rval.set_corner_pos(*next_pos_iterator.__next__())

        # greedy position edge vars
        def get_next_variable_cell() -> (float, float):
            if self._cell_available[0][0]:
                yield (0, 0)

            for i in range(1, GPS.CELL_AMOUNT):
                if self._cell_available[i][0]:
                    yield (i, 0)

                if self._cell_available[0][i]:
                    yield (0, i)

        for var in self._variables:
            shortest_len = GPS.CELL_AMOUNT * GPS.CELL_SIZE * 2 # the longest possible length is GPS.CELL_AMOUNT * GPS.CELL_SIZE * math.sqrt(2)
            best_cell = None

            for var_cell in get_next_variable_cell():
                var.set_corner_pos(*GPS.cell_to_pos(*var_cell))
                ref_len = var.get_ref().length()

                if ref_len < shortest_len:
                    shortest_len = ref_len
                    best_cell = var_cell

            if best_cell == None:
                raise RuntimeError('GPS.run.get_next_variable_pos: best_pos is None meaning all variable cells are full')

            var.set_corner_pos(*GPS.cell_to_pos(*best_cell))
            self._cell_available[best_cell[0]][best_cell[1]] = False


        local_visualizer.generate_single_png(self._scne.export(), f'{self._scene_name}/', f'sol', f'{self._scene_name}')
