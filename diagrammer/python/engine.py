from ..core import engine

from . import utils

import io, sys


class PythonEngine(engine.DiagrammerEngine):
    def __init__(self):
        engine.DiagrammerEngine.__init__(self)

    def generate_data_for_obj(self, obj: object) -> dict:
        data = {
            'id' : f'{id(obj)}',
            'type_str' : type(obj).__name__,
            'val' : None
        }

        if utils.is_basic_value(obj):
            data['val'] = repr(obj)
        elif utils.is_instance(obj):
            data['val'] = self.generate_data_for_obj(obj.__dict__)
            data['val']['obj_type'] = 'class' if data['type_str'] == 'type' else 'obj'
        else:
            collection_type_info = utils.is_collection(obj)

            if collection_type_info != None:
                collection_type, ordering = collection_type_info

                if collection_type == utils.CollectionTypes.LINEAR:
                    data['val'] = []

                    for element in obj:
                        data['val'].append(self.generate_data_for_obj(element))
                elif collection_type == utils.CollectionTypes.MAPPING:
                    data['val'] = {}

                    for key, value in obj.items():
                        data['val'][key] = self.generate_data_for_obj(value)

        return data

    def run(self, code: str, flags: [int]):
        self._bare_language_data = []

        lines = code.split('\n')
        exec_builtins = __builtins__

        current_flag = 0

        str_stdout = io.StringIO()

        def generate_data_for_flag(global_contents: dict, local_contents: dict, error: bool):
            '''Convert Python globals() and locals() to bare language data'''

            nonlocal self
            nonlocal current_flag
            nonlocal str_stdout

            next_flag_data = {
                'scenes' : {
                    'globals' : {name : self.generate_data_for_obj(obj) for name, obj in global_contents.items() if id(obj) != id(exec_builtins)},
                    'locals' : {name : self.generate_data_for_obj(obj) for name, obj in local_contents.items() if id(obj) != id(exec_builtins)},
                },
                'output' : str_stdout.getvalue(),
                'error' : error,
            }

            self._bare_language_data.append(next_flag_data)

            current_flag += 1

        exec_builtins['__gen__'] = generate_data_for_flag
        exec_builtins['__strout__'] = str_stdout

        output_redirection_code = 'import sys\nsys.stdout = __strout__\ndel sys'

        code = f'{output_redirection_code}\ntry:\n'

        for i, line in enumerate(lines):
            spaces = '\t'

            if line != '':
                for char in line:
                    if char.isspace():
                        spaces += char
                    else:
                        break

                line = spaces + line.strip() + '\n'

            if i in flags:
                data_generation = f'{spaces}__builtins__["__gen__"](globals(), locals(), False)\n'
                line += data_generation

            code += line

        code  += 'except Exception as e:\n\tprint(f"{type(e).__name__}: {e}")\n\t__builtins__["__gen__"]({}, {}, True)\n'
        exec(code, {'__builtins__' : exec_builtins})
