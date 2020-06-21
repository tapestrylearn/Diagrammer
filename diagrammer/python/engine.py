from ..core import engine

from . import utils

import io, sys, types


class ModuleProxy(types.ModuleType):
    def __init__(self, name: str, module_contents: dict):
        types.ModuleType.__init__(self, name)

        for key, value in module_contents.items():
            types.ModuleType.__setattr__(self, key, value)
            
    def __getattribute__(self, name: str) -> object:
        if name == '__dict__':
            return types.MappingProxyType(types.ModuleType.__getattribute__(self, '__dict__'))
        elif name in self.__dict__:
            return self.__dict__[name]
            
    def __getattr__(self, name: str) -> object:
        raise AttributeError(f"module '{self.__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: object):
        raise TypeError(f"module '{self.__name__}' does not support attribute assignment")

    def __delattr__(self, name: str):
        raise TypeError(f"module '{self.__name__}' does not support attribute deletion")


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
        exec_builtins = types.ModuleType('__builtins__')

        import builtins

        for key, value in builtins.__dict__.items():
            exec_builtins.__dict__[key] = value

        blacklist = {id(exec_builtins)}

        def generate_data_for_flag(global_contents: dict, local_contents: dict, output: str, error: str):
            '''Convert Python globals() and locals() to bare language data'''

            nonlocal self
            nonlocal blacklist

            self._bare_language_data.append({
                'scenes' : {
                    'globals' : {name : self.generate_data_for_obj(obj) for name, obj in global_contents.items() if id(obj) not in blacklist},
                    'locals' : {name : self.generate_data_for_obj(obj) for name, obj in local_contents.items() if id(obj) not in blacklist},
                },
                'output' : output,
                'error' : error,
            })

        internal_module = ModuleProxy('__engine_internals', {
            '__gen__' : generate_data_for_flag,
            '__strout__' : io.StringIO(),
            '__strerr__' : io.StringIO(),
            '__globals__' : globals,
            '__locals__' : locals,
        })

        blacklist.add(id(internal_module))

        import sys

        builtin_stdout = sys.stdout
        sys.stdout = internal_module.__strout__

        builtin_stderr = sys.stderr
        sys.stderr = internal_module.__strerr__

        to_exec = ''

        for i, line in enumerate(lines):
            spaces = ''

            if line != '':
                for char in line:
                    if char.isspace():
                        spaces += char
                    else:
                        break

                line = spaces + line.strip() + '\n'

            if i in flags:
                data_generation = f'{spaces}__engine_internals.__gen__(__engine_internals.__globals__(), __engine_internals.__locals__(), __engine_internals.__strout__.getvalue(), __engine_internals.__strerr__.getvalue())\n'
                line += data_generation

            to_exec += line

        try:
            exec(to_exec, {'__builtins__' : exec_builtins, '__engine_internals' : internal_module})
        except Exception as e:
            print(f'{e.__class__.__name__}: {e}', file=internal_module.__strerr__)
            internal_module.__gen__({}, {}, internal_module.__strout__.getvalue(), internal_module.__strerr__.getvalue())
        finally:
            sys.stdout = builtin_stdout
            sys.stderr = builtin_stderr
