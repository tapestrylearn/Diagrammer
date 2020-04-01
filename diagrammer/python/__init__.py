import model


def generate_diagrams(session: dict, code: str, flags: [int]) -> dict:
    session['diagrams'] = _run_code(code, flags)

    return session['diagrams'][0].export()['locals']


def _run_code(code: str, flags: [int]) -> [model.Snapshot]:
    lines = code.split('\n')
    _run_code.snapshots = []

    # todo -- create & use blacklist
    _run_code.blacklist = set()

    for i, line in enumerate(lines):
        if i in flags:
            spaces = ''
            
            for char in line:
                if char.isspace():
                    spaces += char
                else:
                    break

            global_declaration = spaces + 'global _run_code'
            global_pruning = spaces + 'global_contents = {name : value for name, value in globals().items() if id(value) not in _run_code.blacklist}'
            local_pruning = spaces + 'local_contents = {name : value for name, value in locals().items() if id(value) not in _run_code.blacklist}'
            snapshot_creation = spaces + '_run_code.snapshots.append(model.Snapshot(global_contents, local_contents))'

            code = '\n'.join(lines[:i + 1] + [global_declaration, global_pruning, local_pruning, snapshot_creation] + lines[i + 1:])
    
    exec(code)

    return _run_code.snapshots


def retrieve_diagram(session: dict, index: int, path: str) -> dict:
    snapshot = session['diagrams'][index]
    
    return snapshot.export()[path]

