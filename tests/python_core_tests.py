import utils
utils.setup_pythonpath_for_tests()

from diagrammer import python as py_diagrammer

import unittest
import json


class DiagrammerPythonCoreTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic_diagram_generation(self):
        diagram_data = py_diagrammer.generate_diagrams_for_code('x = [1, 2, 3]', [0])

        self.assertEqual(len(diagram_data), 1)
        self.assertEqual(diagram_data[0].keys(), {'scenes', 'output', 'error'})
        self.assertEqual(diagram_data[0]['scenes'].keys(), {'globals', 'locals'})
        self.assertEqual(diagram_data[0]['output'], '')
        self.assertEqual(diagram_data[0]['error'], '')
        self.assertEqual(1, 2, json.dumps(diagram_data, indent = 1))


    def test_conditional_diagram_generation(self):
        diagram_data = py_diagrammer.generate_diagrams_for_code('if True:\n\tx = 1', [1])

        self.assertEqual(len(diagram_data), 1)
        self.assertEqual(diagram_data[0].keys(), {'scenes', 'output', 'error'})
        self.assertEqual(diagram_data[0]['scenes'].keys(), {'globals', 'locals'})
        self.assertEqual(diagram_data[0]['output'], '')
        self.assertEqual(diagram_data[0]['error'], '')


    def test_iterative_diagram_generation(self):
        diagram_data = py_diagrammer.generate_diagrams_for_code('for i in range(5):\n\tpass', [1])

        self.assertEqual(len(diagram_data), 5)

        for diagram in diagram_data:
            self.assertEqual(diagram.keys(), {'scenes', 'output', 'error'})
            self.assertEqual(diagram['scenes'].keys(), {'globals', 'locals'})
            self.assertEqual(diagram['output'], '')
            self.assertEqual(diagram['error'], '')


    def test_collection_iterative_diagram_generation(self):
        diagram_data = py_diagrammer.generate_diagrams_for_code('l = []\nfor i in range(5):\n\tl.append(i)', [2])

        self.assertEqual(len(diagram_data), 5)

        for diagram in diagram_data:
            self.assertEqual(diagram.keys(), {'scenes', 'output', 'error'})
            self.assertEqual(diagram['scenes'].keys(), {'globals', 'locals'})
            self.assertEqual(diagram['output'], '')
            self.assertEqual(diagram['error'], '')


    def test_basic_output_generation(self):
        diagram_data = py_diagrammer.generate_diagrams_for_code('print(5)', [0])

        self.assertEqual(diagram_data[0]['output'], '5\n')
        self.assertEqual(diagram_data[0]['error'], '')


    def test_complex_output_generation(self):
        iterations = 5
        diagram_data = py_diagrammer.generate_diagrams_for_code(f'for i in range({iterations}):\n\tprint(i)', [1])

        self.assertEqual(len(diagram_data), iterations)

        expected_output = ''

        for i, snapshot in enumerate(diagram_data):
            expected_output += f'{i}\n'

            self.assertEqual(snapshot['output'], expected_output)
            self.assertEqual(snapshot['error'], '')


if __name__ == '__main__':
    unittest.main()
