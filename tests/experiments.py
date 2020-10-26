import utils
utils.setup_pythonpath_for_tests()

import json
import unittest
from diagrammer.python import scene
import local_visualizer

scne = scene.PyScene(scene.PySceneSettings())
'''scne.construct({
    'a': {'id': 0, 'type_str': 'list', 'val': [
        {'id': 1, 'type_str': 'list', 'val': [
            {'id': 0, 'type_str': 'list', 'val': 'no'}
        ]}
    ]},
    'b': {'id': 1, 'type_str': 'list', 'val': [
        {'id': 0, 'type_str': 'list', 'val': [
            {'id': 1, 'type_str': 'list', 'val': 'no'}
        ]}
    ]}
})'''
scne.construct({
    'a': {'id': 0, 'type_str': 'list', 'val': [
        {'id': 0, 'type_str': 'list', 'val': 'no'}
    ]}
})

scne.gps()
exported = scne.export()
print(json.dumps(exported, indent=2))
local_visualizer.generate_single_png(exported['contents'], '', 'globals', '')
