import utils
utils.setup_pythonpath_for_tests()

from diagrammer.python import gps
from diagrammer.python import scene

import unittest

class PythonGPSTests(unittest.TestCase):
    def setUp(self):
        self._scene = scene.PyScene(scene.PySceneSettings())

    def test_test(self):
        str_bld = {'id': 0, 'type_str': 'str', 'val': "'hello world'"}
        gps.print_basic_value(self._scene.create_value(str_bld))

if __name__ == '__main__':
    unittest.main(verbosity=2) # make tests verbose
