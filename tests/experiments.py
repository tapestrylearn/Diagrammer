import utils
utils.setup_pythonpath_for_tests()

import diagrammer.python
import json

if __name__ == '__main__':
    code = 'a = 1\nb = 1\nc = "str"'

    diagram_data = diagrammer.python.generate_diagrams_for_code(code, [2])
    print(json.dumps(diagram_data, indent = 2))
