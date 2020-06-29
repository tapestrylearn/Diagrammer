import utils
utils.setup_pythonpath_for_tests()

from diagrammer import python as py_diagrammer

if __name__ == '__main__':
    diagram_data = py_diagrammer.generate_diagrams_for_code('x = [1, 2, 3]\ny = x\nz = "abc"', [2])
