from . import model, engine, scene

def generate_diagrams_for_code(code: str, flags: [int]) -> dict:
    engine = PythonEngine()
    engine.run(code, flags)

    