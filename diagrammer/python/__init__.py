from . import model


def generate_diagrams(session: dict, code: str, flags: [int]) -> dict:
    session['diagrams'] = [snapshot.export() for snapshot in _run_code(code, flags)]

    return session['diagrams'][0]


def _run_code(code: str, flags: [int]) -> [model.Snapshot]:
    lines = code.split('\n')
    snapshots = []

    exec_builtins = __builtins__

    def create_snapshot(global_contents: dict, local_contents: dict):
        nonlocal snapshots

        snapshots.append(model.Snapshot(
            {name : value for name, value in global_contents.items() if id(value) != id(exec_builtins)},
            {name : value for name, value in local_contents.items() if id(value) != id(exec_builtins)}
        ))

    exec_builtins['create_snapshot'] = create_snapshot

    for i, line in enumerate(lines):
        if i in flags:
            spaces = ''
            
            for char in line:
                if char.isspace():
                    spaces += char
                else:
                    break

            snapshot_creation = spaces + '__builtins__["create_snapshot"](globals(), locals())'

            code = '\n'.join(lines[:i + 1] + [snapshot_creation] + lines[i + 1:])

    exec(code, {'__builtins__' : exec_builtins})

    return snapshots


def retrieve_diagram(session: dict, index: int) -> dict:    
    return session['diagrams'][index]

    