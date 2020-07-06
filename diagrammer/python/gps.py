from . import scene, local_visualizer
import random
import copy
from collections import defaultdict
import json
import math


# NOTE: GPS can access internal vars of PyScene since it's pretty much an internal class, it's just in its own module because there's so much code

# FITNESS FUNCTIONS
def get_num_colliding_shapes(scne: scene.PyScene) -> int:
    num_colliding_shapes = 0

    for i in range(len(scne._positionable_objects)):
        for j in range(i + 1, len(scne._positionable_objects)):
            if scne._positionable_objects[i].collides(scne._positionable_objects[j]):
                num_colliding_shapes += 1

    return num_colliding_shapes

def get_num_intersecting_lines(scne: scene.PyScene) -> int:
    num_intersecting_lines = 0

    for i in range(len(scne._references)):
        for j in range(i + 1, len(scne._references)):
            if scne._references[i].intersects_arrow(scne._references[j]):
                num_intersecting_lines += 1

    return num_intersecting_lines

def get_num_lines_through_shapes(scne: scene.PyScene) -> int:
    num_lines_through_shapes = 0

    for base_obj in scne._positionable_objects:
        refs_to_check = []
        objs_to_ignore = {base_obj}

        if type(base_obj) == scene.PyVariable:
            refs_to_check.append(base_obj.get_ref())
            objs_to_ignore.add(base_obj.get_head_obj())
        elif type(base_obj) == scene.PySimpleCollection or type(base_obj) == scene.PyNamespaceCollection:
            for var in base_obj.get_contents():
                refs_to_check.append(var.get_ref())
                objs_to_ignore.add(var.get_head_obj())
        elif type(base_obj) == scene.PyNamespace:
            for var in base_obj.get_coll().get_contents():
                refs_to_check.append(var.get_ref())
                objs_to_ignore.add(var.get_head_obj())

        for ref in refs_to_check:
            for pos_obj in scne._positionable_objects:
                if pos_obj not in objs_to_ignore and ref.intersects_shape(pos_obj):
                    num_lines_through_shapes += 1

    return num_lines_through_shapes

def get_collision_index(scne: scene.PyScene) -> int:
    return get_num_intersecting_lines(scne) * 1 + get_num_lines_through_shapes(scne) * 8

# CONSTRAINTS


class PositionArray:
    def __init__(self, coord_amount: int, length: int, obj_sizes: [(int, int)]) -> None:
        self._coord_amount = coord_amount
        self._coord_available = [[True for _ in range(self._coord_amount)] for _ in range(self._coord_amount)]
        self._obj_sizes = obj_sizes
        self._position_array = []

        for i in range(length):
            while True:
                coord = (random.randrange(self._coord_amount), random.randrange(self._coord_amount))

                if self._coord_available[coord[0]][coord[1]]:
                    break

            self._position_array.append(coord)
            self._change_available(i, coord, False)

    def _change_available(self, index: int, base_coord: (int, int), change_to: bool):
        obj_size = self._obj_sizes[index]

        for dx in range(obj_size[0]):
            for dy in range(obj_size[1]):
                target_x = base_coord[0] + dx
                target_y = base_coord[1] + dy

                if target_x < self._coord_amount and target_y < self._coord_amount:
                    self._coord_available[target_x][target_y] = change_to

    def swap_random(self) -> None:
        i = random.randrange(len(self._position_array))

        while True:
            j = random.randrange(len(self._position_array))

            if j != i:
                break

        self._position_array[i], self._position_array[j] = self._position_array[j], self._position_array[i]

    def teleport_random(self) -> None:
        i = random.randrange(len(self._position_array))

        while True:
            new_coord = (random.randrange(self._coord_amount), random.randrange(self._coord_amount))

            if self._coord_available[new_coord[0]][new_coord[1]]:
                break

        old_coord = self._position_array[i]
        self._change_available(i, old_coord, True)
        self._change_available(i, new_coord, False)
        self._position_array[i] = new_coord

    def move_random(self) -> None:
        i = random.randrange(len(self._position_array))
        old_coord = self._position_array[i]

        while True:
            for _ in range(10):
                new_coord = (old_coord[0] + random.randrange(-2, 3), old_coord[1] + random.randrange(-2, 3))

                if 0 <= new_coord[0] < self._coord_amount and 0 <= new_coord[1] < self._coord_amount and self._coord_available[new_coord[0]][new_coord[1]]:
                    break

            break

        self._change_available(i, old_coord, True)
        self._change_available(i, new_coord, False)
        self._position_array[i] = new_coord

    def __iter__(self) -> 'iter':
        return iter(self._position_array)

    def __getitem__(self, key: int) -> (int, int):
        return self._position_array[key]

    def __len__(self) -> int:
        return len(self._position_array)


class Solution:
    COORD_AMOUNT = 10
    COORD_SIZE = 80

    def __init__(self, scne: scene.PyScene, fitness_functions: ['(PyScene) -> numeric'], constraint_functions: ['(PyScene) -> bool']):
        self._scne = scne

        # position PyVariables in scne
        for i, var in enumerate(self._scne._variables):
            var.set_corner_pos((Solution.COORD_SIZE - scene.PyVariable.SIZE) / 2, (Solution.COORD_SIZE - scene.PyVariable.SIZE) / 2 + Solution.COORD_SIZE * i)

        obj_sizes = []

        for rval in self._scne._positionable_rvalues:
            obj_sizes.append((math.ceil(rval.get_width() / Solution.COORD_SIZE), math.ceil(rval.get_height() / Solution.COORD_SIZE)))

        self._position_array = PositionArray(Solution.COORD_AMOUNT, len(self._scne._positionable_rvalues), obj_sizes)

        self.apply()

        self._fitness_scores = []

        for func in fitness_functions:
            self._fitness_scores.append(func(scne))

        self._legal = True

        for func in constraint_functions:
            if func(scne):
                self._legal = False
                break

        self._np = 0
        self._Sp = set()

    def apply(self) -> None:
        for scene_obj, position in zip(self._scne._positionable_rvalues, self._position_array):
            scene_obj.set_corner_pos(Solution.COORD_SIZE + position[0] * Solution.COORD_SIZE, position[1] * Solution.COORD_SIZE)

    def inc_np(self, amount: int) -> None:
        self._np += amount

    def add_to_Sp(self, solution: 'Solution') -> None:
        self._Sp.add(solution)

    def set_front_num(self, front_num: int) -> None:
        self._front_num = front_num

    def get_front_num(self) -> int:
        return self._front_num

    def get_position_array(self) -> [(float, float)]:
        return self._position_array

    def get_position(self, index: int) -> (float, float):
        return self._position_array[index]

    def np(self) -> int:
        return self._np

    def Sp(self) -> {'Solution'}:
        return self._Sp

    def dominates(self, other: 'Solution') -> bool:
        if self._legal and not other._legal:
            return True
        elif not self._legal and other._legal:
            return False
        else:
            return all([self._fitness_scores[i] < other._fitness_scores[i] for i in range(len(self._fitness_scores))])

    def weird_id(self) -> str:
        return str(hex(id(self)))[-4:]

    def __str__(self) -> str:
        return f'id: {self.weird_id()}, np: {self._np}, Sp: [{", ".join([sol.weird_id() for sol in self._Sp])}]'


# MAIN ALGORITHM
class GPS:
    GENERATION_NUM = 10
    POP_SIZE = 10
    FITNESS_FUNCTIONS = [get_collision_index]
    CONSTRAINT_FUNCTIONS = []
    MUTATION_CHANCE = 0.5
    MUTATION_MAG = 50
    CANVAS_SIZE = 500

    def __init__(self, scne: scene.PyScene, scene_name: str):
        print(scene_name)
        self._scne = scne
        self._scene_name = scene_name
        self._solutions = list()

        for _ in range(GPS.POP_SIZE):
            self._solutions.append(Solution(self._scne, GPS.FITNESS_FUNCTIONS, GPS.CONSTRAINT_FUNCTIONS))

        self._fronts = defaultdict(set)

    def run(self) -> None:
        local_visualizer.remove_base_dir()

        for g in range(GPS.GENERATION_NUM):
            self._non_dominated_sort()
            self._select()
            self._asexual_repopulate()

            # generate images
            for front_num, front in self._fronts.items():
                for s, sol in enumerate(front):
                    sol.apply()
                    local_visualizer.generate_single_png(self._scne.export(), f'{self._scene_name}/gen{g}/front{front_num}', f'sol{s}', ', '.join([str(score) for score in sol._fitness_scores]))

    def _non_dominated_sort(self) -> None:
        # generate np and Sp
        for t, this in enumerate(self._solutions):
            for o, other in enumerate(self._solutions):
                if this.dominates(other):
                    this.add_to_Sp(other)
                    other.inc_np(1)

        # sort
        current_front = 0
        s = 0
        self._fronts = defaultdict(set)

        while s < len(self._solutions):
            sol = self._solutions[s]

            if sol.np() == 0:
                self._add_to_front(current_front, sol)
            else:
                s += 1

        while len(self._solutions) != 0:
            for sol in self._fronts[current_front]:
                for dominated_sol in sol._Sp:
                    dominated_sol.inc_np(-1)

                    if dominated_sol.np() == 0:
                        self._add_to_front(current_front + 1, dominated_sol)

            current_front += 1

    def _select(self) -> None:
        for front in self._fronts.values():
            for sol in front:
                self._solutions.append(sol)

                if len(self._solutions) >= GPS.POP_SIZE / 2:
                    return

    def _asexual_repopulate(self) -> None:
        child_solutions = []

        while len(child_solutions) < GPS.POP_SIZE - len(self._solutions):
            # pick one parent
            '''
            candidate0 = self._solutions[random.randrange(len(self._solutions))]

            while True:
                candidate1 = self._solutions[random.randrange(len(self._solutions))]

                if candidate1 != candidate0:
                    break

            if candidate0.get_front_num() < candidate1.get_front_num():
                parent = candidate0
            else:
                parent = candidate1
            '''

            parent = self._solutions[random.randrange(len(self._solutions))]

            # duplicate parent
            child = copy.deepcopy(parent)

            # mutate child
            for _ in range(len(child.get_position_array())):
                if random.random() < GPS.MUTATION_CHANCE:
                    child.get_position_array().swap_random()

                if random.random() < GPS.MUTATION_CHANCE:
                    child.get_position_array().move_random()

            # add child object to child_solutions
            child_solutions.append(child)

        # mutate everything in self._solutions as well
        for sol in self._solutions:
            for _ in range(len(sol.get_position_array())):
                if random.random() < GPS.MUTATION_CHANCE:
                    sol.get_position_array().swap_random()

                if random.random() < GPS.MUTATION_CHANCE:
                    sol.get_position_array().move_random()

        # finally, combine children and parents
        self._solutions.extend(child_solutions)

    def _sexual_repopulate(self) -> None:
        child_solutions = []

        while len(child_solutions) < GPS.POP_SIZE - len(self._solutions):
            # pick parents
            candidate0 = self._solutions[random.randrange(len(self._solutions))]

            while True:
                candidate1 = self._solutions[random.randrange(len(self._solutions))]

                if candidate1 != candidate0:
                    break

            if candidate0.get_front_num() < candidate1.get_front_num():
                parent0 = candidate0
            else:
                parent0 = candidate1

            while True:
                candidate0 = self._solutions[random.randrange(len(self._solutions))]

                if candidate0 != parent0:
                    break

            while True:
                candidate1 = self._solutions[random.randrange(len(self._solutions))]

                if candidate1 != candidate0 and candidate1 != parent0:
                    break

            if candidate0.get_front_num() < candidate1.get_front_num():
                parent1 = candidate0
            else:
                parent1 = candidate1

            # create child_position_array with shuffled genes
            gene_indices = [i for i in range(len(parent0.get_position_array()))]
            random.shuffle(gene_indices)
            child_position_array = [None] * len(gene_indices)

            for gene_index in gene_indices:
                if gene_index < len(gene_indices) / 2:
                    child_position_array[gene_index] = parent0.get_position(gene_index)
                else:
                    child_position_array[gene_index] = parent1.get_position(gene_index)

            # mutate child
            mutate_set = False

            if (mutate_set):
                for gene_index in range(len(child_position_array)):
                    if random.random() < GPS.MUTATION_CHANCE:
                        child_position_array[gene_index] = (random.random() * GPS.CANVAS_SIZE, random.random() * GPS.CANVAS_SIZE)
            else:
                for gene_index in range(len(child_position_array)):
                    if random.random() < GPS.MUTATION_CHANCE:
                        pos = child_position_array[gene_index]
                        child_position_array[gene_index] = (pos[0] + random.randrange(GPS.MUTATION_MAG), pos[1] + random.randrange(GPS.MUTATION_MAG))

            # add child object to child_solutions
            child_solutions.append(Solution(self._scne, child_position_array, GPS.FITNESS_FUNCTIONS, GPS.CONSTRAINT_FUNCTIONS))

        self._solutions.extend(child_solutions)

    def _add_to_front(self, front_num: int, sol: Solution) -> None:
        self._fronts[front_num].add(sol)
        self._solutions.remove(sol)
        sol.set_front_num(front_num)
