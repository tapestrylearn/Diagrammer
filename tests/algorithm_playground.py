import utils
utils.setup_pythonpath_for_tests()

from diagrammer import python as py_diagrammer

if __name__ == '__main__':
    code_str = 'l1 = [[1, 2], 2, 3]\nl2 = [1, [1, 2, 3]]\na = 5'

    diagram_data = py_diagrammer.generate_diagrams_for_code(code_str, [len(code_str.split('\n')) - 1])
