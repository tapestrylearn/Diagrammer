from . import model


def generate_diagrams(session: dict, code: str, flags: [int]) -> dict:
    diagrams = _run_code(code, flags)
    session['diagrams'] = [diagram.export() for diagram in diagrams]

    return session['diagrams'][0]


def _run_code(code: str, flags: [int]) -> [model.Snapshot]:
    pass


def retrieve_diagram(session: dict, index: int, path: str) -> (dict, dict):
    snapshot_data = session['diagrams'][index]
    
    return (snapshot.get_diagram(path), snapshot.generate_path_tree())


def _find_diagram_for_path(snapshot_data: dict, path: str) -> dict:
    path_pieces = path.split(':')

    child = snapshot_data

    for segment in path_pieces:
        child = snapshot_data[segment]

    return child