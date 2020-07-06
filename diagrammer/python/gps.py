from . import scene, local_visualizer
import random


# NOTE: GPS can access internal vars of PyScene since it's pretty much an internal class, it's just in its own module because there's so much code

# MAIN ALGORITHM
class GPS:
    CANVAS_SIZE = 500

    def __init__(self, scne: scene.PyScene, scene_name: str):
        self._scne = scne
        self._scene_name = scene_name

    def run(self) -> None:
        for scene_obj in self._scne._positionable_objects:
            scene_obj.set_corner_pos(random.random() * GPS.CANVAS_SIZE, random.random() * GPS.CANVAS_SIZE)

        local_visualizer.generate_single_png(self._scne.export(), f'{self._scene_name}/', f'sol', f'{self._scene_name}')
