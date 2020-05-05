import utils
utils.setup_pythonpath_for_tests()

from diagrammer import python as py_diagrammer

import unittest


class DiagrammerPythonCoreTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic_diagram_generation(self):
        diagram_data = py_diagrammer.generate_diagrams_for_code('x = 1', [0])

        self.assertEqual(len(diagram_data), 1)
        self.assertEqual(diagram_data[0].keys(), {'globals', 'locals', 'output'})
        self.assertEqual(diagram_data[0]['globals'].keys(), {'variables', 'values'})
        self.assertEqual(diagram_data[0]['locals'].keys(), {'variables', 'values'})
        self.assertEqual(diagram_data[0]['output'], '')


    def test_basic_output_generation(self):
        diagram_data = py_diagrammer.generate_diagrams_for_code('print(5)', [0])
        self.assertEqual(diagram_data[0]['output'], '5\n')

    def test_complex_output_generation(self):
        iterations = 5
        diagram_data = py_diagrammer.generate_diagrams_for_code(f'for i in range({iterations}):\n\tprint(i)', [1])

        self.assertEqual(len(diagram_data), iterations)

        expected_output = ''

        for i, snapshot in enumerate(diagram_data):
            expected_output += f'{i}\n'
            self.assertEqual(snapshot['output'], expected_output)


if __name__ == '__main__':
    unittest.main()