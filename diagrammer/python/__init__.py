from . import engine, scene, gps

def generate_diagrams_for_code(code: str, flags: [int], **settings) -> dict:
    py_engine = engine.PythonEngine()
    py_engine.run(code, flags)

    diagram_data = []

    for snapshot_data in py_engine.get_bare_language_data():
        globals_data, locals_data = (snapshot_data['scenes']['globals'], snapshot_data['scenes']['locals'])
        snapshot = scene.PySnapshot(globals_data, locals_data, snapshot_data['output'], snapshot_data['error'], scene.PySceneSettings.from_dict(settings))

        for name, scne in snapshot.get_scenes().items():
            my_gps = gps.GPS(scne, name)
            my_gps.run()

        diagram_data.append(snapshot.export())

    return diagram_data
