from . import model, engine, scene

def generate_diagrams_for_code(code: str, flags: [int]) -> dict:
    py_engine = engine.PythonEngine()
    py_engine.run(code, flags)

    diagram_data = []

    for snapshot_data in py_engine.get_bare_language_data():
        globals_data, locals_data = (snapshot_data['globals'], snapshot_data['locals'])
        snapshot = scene.PySnapshot(globals_data, locals_data)

        diagram_data.append(snapshot.export())

    return diagram_data