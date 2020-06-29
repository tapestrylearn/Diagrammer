from . import scene, local_visualizer
import random


# MAIN ALGORITHM
# note: gps can access internal vars of PyScene since it's a pretty internal function, it's just in its own module because there's so much code
def gps(scne: scene.PyScene, scene_name: str) -> None:
    # initialize
    iteration_num = 10
    position_array = []

    for _ in range(len(scne._positionable_objects)):
        position_array.append((random.random() * 500, random.random() * 500))

    for i in range(iteration_num):
        # apply input
        _apply_position_array(scne, position_array)
        local_visualizer.generate_single_png(scne.export(), f'{scene_name}/gen{i}', 'img')

        # calculate fitness
        print(f'scene {scene_name} generation {i} num intersections: {get_num_intersections(scne)}')

        # get new input
        position_array = []

        for _ in range(len(scne._positionable_objects)):
            position_array.append((random.random() * 500, random.random() * 500))


def _apply_position_array(scne: scene.PyScene, position_array: [(float, float)]) -> None:
    for scene_obj, position in zip(scne._positionable_objects, position_array):
        scene_obj.set_corner_pos(*position)


# FITNESS FUNCTIONS
def get_num_intersections(scne: scene.PyScene) -> int:
    num_intersections = 0

    for i in range(len(scne._references)):
        for j in range(i + 1, len(scne._references)):
            if scne._references[i].intersects(scne._references[j]):
                num_intersections += 1

    return num_intersections


# CONSTRAINTS
