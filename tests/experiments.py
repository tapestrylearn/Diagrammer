import utils
utils.setup_pythonpath_for_tests()

from diagrammer import python as py_diagrammer
import json
import os


data = py_diagrammer.generate_diagrams_for_code('x = 1\n', [1], py_diagrammer.scene.PySceneSettings())
console_print(json.dumps(data, indent = 1))
