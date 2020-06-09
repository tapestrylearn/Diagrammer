import sys

def setup_pythonpath_for_tests():
    # Add the Diagrammer workspace directory to PYTHONPATH
    # Run this before importing any Diagrammer code in any test file
    file_segments = __file__.split('/')
    sys.path.append('/'.join(file_segments[:-2]))
