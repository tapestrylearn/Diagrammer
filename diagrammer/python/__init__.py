from . import model


def generate_diagrams(session: dict, code: str, flags: [int]) -> dict:
    session['diagrams'] = _run_code(code, flags)

    return session['diagrams'][0].export()['locals']


def _run_code(code: str, flags: [int]) -> [model.Snapshot]:
    pass


def retrieve_diagram(session: dict, index: int, path: str) -> dict:
    snapshot = session['diagrams'][index]
    
    return snapshot.export()[path]

