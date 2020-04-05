import model


def generate_diagrams(session: dict, code: str, flags: [int]) -> dict:
    session['diagrams'] = _run_code(code, flags)

    return session['diagrams'][0].export()['locals']


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

    # todo -- create & use blacklist
    # issue -- globals "cleanup" after running code, primitive exclusion
    #  possible solution -- contain snapshots and blacklist in namespace of _run_code to separate from actual code
    # issue -- primitive exclusion still includes certain values
    #   possible solution: switch to manual blacklist of internal python names and local vars in _run_code

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


def retrieve_diagram(session: dict, index: int, path: str) -> dict:
    snapshot = session['diagrams'][index]
    
    return snapshot.export()[path]

