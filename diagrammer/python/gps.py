from . import scene, local_visualizer
import random
from collections import defaultdict


# FITNESS FUNCTIONS
def get_num_intersections(scne: scene.PyScene) -> int:
    num_intersections = 0

    for i in range(len(scne._references)):
        for j in range(i + 1, len(scne._references)):
            if scne._references[i].intersects(scne._references[j]):
                num_intersections += 1

    return num_intersections


# CONSTRAINTS


class Solution:
    def __init__(self, scne: scene.PyScene, position_array: [(float, float)], fitness_functions: ['(PyScene) -> numeric']):
        self._scne = scne
        self._position_array = position_array

        self.apply()

        self._fitness_scores = []

        for func in fitness_functions:
            self._fitness_scores.append(func(scne))

        self._np = 0
        self._Sp = set()

    def apply(self) -> None:
        for scene_obj, position in zip(self._scne._positionable_objects, self._position_array):
            scene_obj.set_corner_pos(*position)

    def inc_np(self, amount: int) -> None:
        self._np += amount

    def add_to_Sp(self, solution: 'Solution') -> None:
        self._Sp.add(solution)

    def np(self) -> int:
        return self._np

    def Sp(self) -> {'Solution'}:
        return self._Sp

    def dominates(self, other: 'Solution') -> bool:
        return all([self._fitness_scores[i] < other._fitness_scores[i] for i in range(len(self._fitness_scores))])


# MAIN ALGORITHM
# note: GPS can access internal vars of PyScene since it's pretty much an internal class, it's just in its own module because there's so much code
class GPS:
    GENERATION_NUM = 1
    POP_SIZE = 5
    FITNESS_FUNCTIONS = [get_num_intersections]

    def __init__(self, scne: scene.PyScene, scene_name: str):
        print(scene_name)
        self._scne = scne
        self._scene_name = scene_name
        self._solutions = list()

        for _ in range(GPS.POP_SIZE):
            position_array = []

            for _ in range(len(self._scne._positionable_objects)):
                position_array.append((random.random() * 500, random.random() * 500))

            self._solutions.append(Solution(self._scne, position_array, GPS.FITNESS_FUNCTIONS))

        self._fronts = defaultdict(set)

    def run(self) -> None:
        for g in range(GPS.GENERATION_NUM):
            # sort
            self._non_dominated_sort()

            # generate images
            for front_num, front in self._fronts.items():
                for s, sol in enumerate(front):
                    sol.apply()
                    local_visualizer.generate_single_png(self._scne.export(), f'{self._scene_name}/gen{g}/front{front_num}', f'sol{s}', f'{sol._fitness_scores[0]}')

    def _non_dominated_sort(self) -> None:
        print('called nds')

        # generate np and Sp
        for t, this in enumerate(self._solutions):
            for o, other in enumerate(self._solutions):
                if this.dominates(other):
                    this.add_to_Sp(other)
                    other.inc_np(1)

        for sol in self._solutions:
            print(f'np: {sol.np()}, Sp: {sol.Sp()}')

        # sort
        # front 0
        current_front = 0
        print('\nwhile start')

        for sol in self._solutions:
            print(f'np: {sol.np()}, Sp: {sol.Sp()}')

        print('solutions', self._solutions)
        print('fronts', self._fronts)
        print('current_front', current_front)

        for sol in self._solutions:
            if sol.np() == 0:
                self._add_to_front(current_front, sol)

                for dominated_sol in sol._Sp:
                    dominated_sol.inc_np(-1)

                    if dominated_sol.np() == 0:
                        self._add_to_front(current_front + 1, dominated_sol)

        # other fronts
        current_front += 1

        while len(self._solutions) != 0:
            print('\nwhile start')

            for sol in self._solutions:
                print(f'np: {sol.np()}, Sp: {sol.Sp()}')

            print('solutions', self._solutions)
            print('fronts', self._fronts)
            print('current_front', current_front)

            for sol in self._fronts[current_front]:
                for dominated_sol in sol._Sp:
                    dominated_sol.inc_np(-1)

                    if dominated_sol.np() == 0:
                        self._add_to_front(current_front + 1, dominated_sol)

            current_front += 1

    def _add_to_front(self, front_num: int, sol: Solution) -> None:
        self._fronts[front_num].add(sol)
        self._solutions.remove(sol)
