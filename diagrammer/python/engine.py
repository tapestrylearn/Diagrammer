from ..core import engine

from . import utils

import io, sys, types


class ModuleProxy(types.ModuleType):
    def __init__(self, name: str, module_contents: dict):
        types.ModuleType.__init__(self, name)

        self.__dict__ = types.MappingProxyType(module_contents)

    def __setattr__(self, name: str, value: object):
        raise TypeError(f"module {self.__name__} does not support item assignment")

    def __delattr(self, name: str):
        raise TypeError(f"module {self.__name__} does not support item deletion")


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

    def generate_data_for_flag(global_contents: dict, local_contents: dict, output: str, error: str):
        '''Convert Python globals() and locals() to bare language data'''

        next_flag_data = {
            'scenes' : {
                'globals' : {name : self.generate_data_for_obj(obj) for name, obj in global_contents.items()},
                'locals' : {name : self.generate_data_for_obj(obj) for name, obj in local_contents.items()},
            },
            'output' : output,
            'error' : error,
        }

    def run(self, code: str, flags: [int]):
        self._bare_language_data = []

        lines = code.split('\n')
        exec_builtins = __builtins__

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
