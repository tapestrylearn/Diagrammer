from ..core import engine

class PythonEngine(engine.Engine):
    def __init__(self):
        engine.Engine.__init__(self)
        # do any additional setup needed

    def run_code(self, code: str, flags: [int]):
        # run python code (use old core code)
        pass