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
        else:
            raise AttributeError(f"module '{self.__name__}' has no attribute '{name}'")

    def __getattr__(self, name: str) -> object:
        raise AttributeError(f"module '{self.__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: object):
        raise TypeError(f"module '{self.__name__}' does not support attribute assignment")

    def __delattr__(self, name: str):
        raise TypeError(f"module '{self.__name__}' does not support attribute deletion")


class RestrictionError(Exception):
    pass


class BlockedConstruct:
    def __init__(self, name: str):
        self._name = name

    def __call__(self, *args, **kwargs): # take in any amount of args to not raise error for number of args
        raise RestrictionError(f"Illegal attempt to use blocked construct '{self._name}'")


class PythonEngine(engine.DiagrammerEngine):
    BASE_DATA_GENERATION_CODE = '_engine_internals.__gen__(_engine_internals.__globals__(), _engine_internals.__locals__(), _engine_internals.__strout__.getvalue(), _engine_internals.__strerr__.getvalue())'

    def __init__(self):
        engine.DiagrammerEngine.__init__(self)

    def generate_data_for_obj(self, obj: object, strings_in_chain=None, id_string_override=None) -> dict:
        if id_string_override != None:
            id_string = id_string_override
        else:
            id_string = f'{id(obj)}'

        data = {
            'id' : id_string,
            'type_str' : obj.__class__.__name__,
            'val' : None
        }

        if strings_in_chain == None:
            strings_in_chain = set()

        # "base case": if it's self-ref, set None as the value
        if id_string in strings_in_chain:
            return data

        strings_in_chain.add(id_string)

        if utils.is_basic_value(obj):
            data['val'] = repr(obj)
        elif utils.is_instance(obj):
            id_string_override = f'{obj.__name__}->ddict' if data['type_str'] == 'type' else None
            data['val'] = self.generate_data_for_obj(obj.__dict__, strings_in_chain, id_string_override)
            data['val']['obj_type'] = 'class' if data['type_str'] == 'type' else 'obj'
        else:
            collection_type_info = utils.is_collection(obj)

            if collection_type_info != None:
                collection_type, ordering = collection_type_info

                if collection_type == utils.CollectionTypes.LINEAR:
                    data['val'] = []

                    for element in obj:
                        data['val'].append(self.generate_data_for_obj(element, strings_in_chain))
                elif collection_type == utils.CollectionTypes.MAPPING:
                    data['val'] = {}

                    for key, value in obj.items():
                        data['val'][key] = self.generate_data_for_obj(value, strings_in_chain)

        return data

    def run(self, code: str, flags: [int]):
        self._bare_language_data = []

        lines = code.split('\n')
        exec_builtins = types.ModuleType('__builtins__')

        import builtins

        for key, value in builtins.__dict__.items():
            exec_builtins.__dict__[key] = value

        # blacklist
        exec_builtins.__dict__['input'] = BlockedConstruct('input')
        exec_builtins.__dict__['open'] = BlockedConstruct('open')
        exec_builtins.__dict__['exec'] = BlockedConstruct('exec')
        exec_builtins.__dict__['eval'] = BlockedConstruct('eval')

        data_generation_blacklist = {id(exec_builtins)}

        def generate_data_for_flag(global_contents: dict, local_contents: dict, output: str, error: str):
            '''Convert Python globals() and locals() to bare language data'''

            nonlocal self
            nonlocal data_generation_blacklist

            self._bare_language_data.append({
                'scenes' : {
                    'globals' : {name : self.generate_data_for_obj(obj) for name, obj in global_contents.items() if id(obj) not in data_generation_blacklist},
                    'locals' : {name : self.generate_data_for_obj(obj) for name, obj in local_contents.items() if id(obj) not in data_generation_blacklist},
                },
                'output' : output,
                'error' : error,
            })

        engine_internals = ModuleProxy('_engine_internals', {
            '__gen__' : generate_data_for_flag,
            '__strout__' : io.StringIO(),
            '__strerr__' : io.StringIO(),
            '__globals__' : globals,
            '__locals__' : locals,
        })

        data_generation_blacklist.add(id(engine_internals))

        orig_stdout = sys.stdout
        sys.stdout = engine_internals.__strout__

        orig_stderr = sys.stderr
        sys.stderr = engine_internals.__strerr__

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

            # add diagram generation after the line
            to_exec += line

            if i in flags:
                to_exec += f'{spaces}{PythonEngine.BASE_DATA_GENERATION_CODE}\n'

        # add diagram generation at the end no matter what
        to_exec += f'{PythonEngine.BASE_DATA_GENERATION_CODE}\n'

        try:
            exec(to_exec, {'__builtins__' : exec_builtins, '_engine_internals' : engine_internals})
        except Exception as e:
            print(f'{e.__class__.__name__}: {e}', file=engine_internals.__strerr__)
            engine_internals.__gen__({}, {}, engine_internals.__strout__.getvalue(), engine_internals.__strerr__.getvalue())
        finally:
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr
