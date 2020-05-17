from ..core import engine

from . import utils

class PythonEngine(engine.DiagrammerEngine):
    def __init__(self):
        engine.DiagrammerEngine.__init__(self)
        # do any additional setup needed


    def generate_data_for_obj(self, obj: object, scene: str, snapshot: int) -> dict:
        data = {
            'id' : f'{snapshot}-{scene}-{id(obj)}',
            'type_str' : type(obj).__name__,
            'val' : None
        }

        if utils.is_basic_value(obj):
            data['val'] = repr(obj)
        elif utils.is_instance(obj):
            data['val'] = {
                '__dict__' : self.generate_data_for_obj(obj.__dict__)
            }
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

        def generate_data_for_flag(global_contents: dict, local_contents: dict):
            '''Convert Python globals() and locals() to bare language data'''

            nonlocal self
            nonlocal current_flag

            self._bare_language_data.append({
                'globals' : {name : self.generate_data_for_obj(obj, 'globals', current_flag) for name, obj in global_contents.items() if id(obj) != id(exec_builtins)},
                'locals' : {name : self.generate_data_for_obj(obj, 'locals', current_flag) for name, obj in local_contents.items() if id(obj) != id(exec_builtins)},
                'output' : self._output
            })

            current_flag += 1

        def print_to_engine(*objs, sep=' ', end='\n'):
            output = sep.join([str(obj) for obj in objs])
            self._output += output
            self._output += end

        exec_builtins['__gen__'] = generate_data_for_flag
        exec_builtins['print'] = print_to_engine

        for i, line in enumerate(lines):
            if i in flags:
                spaces = ''
                
                for char in line:
                    if char.isspace():
                        spaces += char
                    else:
                        break

                data_generation = spaces + '__builtins__["__gen__"](globals(), locals())'
                code = '\n'.join(lines[:i + 1] + [data_generation] + lines[i + 1:])

        exec(code, {'__builtins__' : exec_builtins})
