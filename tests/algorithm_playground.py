import utils
utils.setup_pythonpath_for_tests()

from diagrammer import python as py_diagrammer

if __name__ == '__main__':
    code_str = 'x = 1\ny = 2\nz = 3'
    diagram_data = py_diagrammer.generate_diagrams_for_code(code_str, [len(code_str.split('\n')) - 1])
