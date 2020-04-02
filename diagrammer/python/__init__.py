import model


def generate_diagrams(session: dict, code: str, flags: [int]) -> dict:
    session['diagrams'] = _run_code(code, flags)

    return session['diagrams'][0].export()['locals']


def _run_code(code: str, flags: [int]) -> [model.Snapshot]:
    lines = code.split('\n')
    snapshots = []

    def create_snapshot(global_contents: dict, local_contents: dict):
        nonlocal snapshots

        print({name for name, value in local_contents.items() if id(value) != id(blacklist) and id(value) in blacklist})
        snapshots.append(model.Snapshot(
            {name : value for name, value in global_contents.items() if id(value) != id(blacklist) and id(value) not in blacklist},
            {name : value for name, value in local_contents.items() if id(value) != id(blacklist) and id(value) not in blacklist}
        ))

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

            snapshot_creation = spaces + 'create_snapshot(globals(), locals())'

            code = '\n'.join(lines[:i + 1] + [snapshot_creation] + lines[i + 1:])

    blacklist = {id(obj) for obj in list(globals().values()) + list(locals().values()) if obj != None and type(obj) not in {int, float, bool, str, complex}}
    exec(code)

    return snapshots


def retrieve_diagram(session: dict, index: int, path: str) -> dict:
    snapshot = session['diagrams'][index]
    
    return snapshot.export()[path]

