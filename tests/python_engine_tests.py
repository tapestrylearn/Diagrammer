import utils
utils.setup_pythonpath_for_tests()

from diagrammer.python import engine

import unittest
import types
import sys
import re


class ModuleProxyTests(unittest.TestCase):
    def setUp(self):
        self.module_contents = {
            '__name__' : 'test',
            '__doc__' : None,
            '__package__' : None,
            '__loader__' : None,
            '__spec__' : None,
            'i' : 1,
            's' : 'hello, world',
            'f' : 2.5,
            'b' : True,
            'fn' : print,
        }
        self.module_proxy = engine.ModuleProxy('test', self.module_contents)

    def test_proxy_getattribute(self):
        self.assertEqual(self.module_proxy.i, self.module_contents['i'])
        self.assertEqual(self.module_proxy.s, self.module_contents['s'])
        self.assertEqual(self.module_proxy.f, self.module_contents['f'])
        self.assertEqual(self.module_proxy.b, self.module_contents['b'])
        self.assertEqual(self.module_proxy.fn, self.module_contents['fn'])
        self.assertEqual(self.module_proxy.__dict__, types.MappingProxyType(self.module_contents))

        with self.assertRaises(AttributeError):
            self.module_proxy.a # invalid attribute

    def test_proxy_setattr(self):
        with self.assertRaises(TypeError):
            self.module_proxy.i = 3

    def test_proxy_delattr(self):
        with self.assertRaises(TypeError):
            del self.module_proxy.i

    def test_proxy_ddict_access(self):
        self.assertEqual(self.module_proxy.__dict__['i'], self.module_contents['i'])
        self.assertEqual(self.module_proxy.__dict__['s'], self.module_contents['s'])
        self.assertEqual(self.module_proxy.__dict__['f'], self.module_contents['f'])
        self.assertEqual(self.module_proxy.__dict__['b'], self.module_contents['b'])
        self.assertEqual(self.module_proxy.__dict__['fn'], self.module_contents['fn'])

        with self.assertRaises(KeyError):
            self.module_proxy.__dict__['a'] # invalid attribute

    def test_proxy_ddict_mutation(self):
        with self.assertRaises(TypeError):
            self.module_proxy.__dict__['i'] = 3

    def test_proxy_ddict_deletion(self):
        with self.assertRaises(TypeError):
            del self.module_proxy.__dict__['i']


class PythonEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = engine.PythonEngine()

    def test_data_generation_basic_value(self):
        int_value = 5
        int_data = {
            'id' : f'{id(int_value)}',
            'type_str' : 'int',
            'val' : '5'
        }

        self.assertEqual(self.engine.generate_data_for_obj(int_value), int_data)

        float_value = 2.5
        float_data = {
            'id' : f'{id(float_value)}',
            'type_str' : 'float',
            'val' : '2.5'
        }

        self.assertEqual(self.engine.generate_data_for_obj(float_value), float_data)

        str_value = 'hello, world'
        str_data = {
            'id' : f'{id(str_value)}',
            'type_str' : 'str',
            'val' : "'hello, world'"
        }

        self.assertEqual(self.engine.generate_data_for_obj(str_value), str_data)

        bool_value = True
        bool_data = {
            'id' : f'{id(bool_value)}',
            'type_str' : 'bool',
            'val' : 'True'
        }

        self.assertEqual(self.engine.generate_data_for_obj(bool_value), bool_data)

        range_value = range(5)
        range_data = {
            'id' : f'{id(range_value)}',
            'type_str' : 'range',
            'val' : 'range(0, 5)'
        }

        self.assertEqual(self.engine.generate_data_for_obj(range_value), range_data)

        func_value = lambda: 10
        func_data = {
            'id' : f'{id(func_value)}',
            'type_str' : 'function',
            'val' : f'{repr(func_value)}',
        }

        self.assertEqual(self.engine.generate_data_for_obj(func_value), func_data)

        # TODO: add tests for other function-like types


    def test_data_generation_linear_collection(self):
        list_value = [1, 2, 3]
        list_data = {
            'id' : f'{id(list_value)}',
            'type_str' : 'list',
            'val' : [
                {
                    'id' : f'{id(list_value[0])}',
                    'type_str' : 'int',
                    'val' : '1'
                },
                {
                    'id' : f'{id(list_value[1])}',
                    'type_str' : 'int',
                    'val' : '2'
                },
                {
                    'id' : f'{id(list_value[2])}',
                    'type_str' : 'int',
                    'val' : '3'
                },
            ]
        }

        self.assertEqual(self.engine.generate_data_for_obj(list_value), list_data)

        tuple_value = (1.1, 2.2, 3.3)
        tuple_data = {
            'id' : f'{id(tuple_value)}',
            'type_str' : 'tuple',
            'val' : [
                {
                    'id' : f'{id(tuple_value[0])}',
                    'type_str' : 'float',
                    'val' : '1.1'
                },
                {
                    'id' : f'{id(tuple_value[1])}',
                    'type_str' : 'float',
                    'val' : '2.2'
                },
                {
                    'id' : f'{id(tuple_value[2])}',
                    'type_str' : 'float',
                    'val' : '3.3'
                },
            ]
        }

        self.assertEqual(self.engine.generate_data_for_obj(tuple_value), tuple_data)

        set_value = {'a', 'b', 'c'}
        set_data = {
            'id' : f'{id(set_value)}',
            'type_str' : 'set',
            'val' : [
                {
                    'id' : f'{id(element)}',
                    'type_str' : type(element).__name__,
                    'val' : repr(element)
                } for element in set_value
            ]
        }

        self.assertEqual(self.engine.generate_data_for_obj(set_value), set_data)


    def test_data_generation_self_ref(self):
        a = []
        a.append(a)
        list_data = {
            'id' : f'{id(a)}',
            'type_str' : 'list',
            'val' : [
                {
                    'id' : f'{id(a)}',
                    'type_str' : 'list',
                    'val' : None
                },
            ]
        }

        self.assertEqual(self.engine.generate_data_for_obj(a), list_data)


    def test_data_generation_mapping_collection(self):
        dict_value = {'a' : 1, 'b' : 2, 'c' : 3}
        dict_data = {
            'id' : f'{id(dict_value)}',
            'type_str' : 'dict',
            'val' : {
                key : {'id' : f'{id(value)}', 'type_str' : type(value).__name__, 'val' : repr(value)} for key, value in dict_value.items()
            },
        }

        self.assertEqual(self.engine.generate_data_for_obj(dict_value), dict_data)


    def test_data_generation_instance(self):
        class Test:
            def __init__(self):
                self.x = 1
                self.y = 2
                self.s = 'hello'

        instance_value = Test()
        instance_data = {
            'id' : f'{id(instance_value)}',
            'type_str' : type(instance_value).__name__,
            'val' : {
                'id' : f'{id(instance_value.__dict__)}',
                'type_str' : 'dict',
                'obj_type' : 'obj',
                'val' : {
                    key : {'id' : f'{id(value)}', 'type_str' : type(value).__name__, 'val' : repr(value)} for key, value in instance_value.__dict__.items()
                },
            }
        }

        self.assertEqual(self.engine.generate_data_for_obj(instance_value), instance_data)

        class_data = {
            'id' : f'{id(Test)}',
            'type_str' : 'type',
            'val' : {
                'id' : f'{type(instance_value).__name__}->ddict',
                'type_str' : type(Test.__dict__).__name__,
                'obj_type' : 'class',
                'val' : {

                }
            }
        }

        generated_class_data = self.engine.generate_data_for_obj(Test)
        generated_class_data['val']['val'] = {}

        self.assertEqual(generated_class_data, class_data)


    def test_code_execution(self):
        simple_code_snippet = 'x=1\ny=2\nz=3\n'
        simple_code_data = [{
            'scenes' : {
                'globals' : {
                    'x' : {
                        'type_str' : 'int',
                        'val' : '1'
                    },
                    'y' : {
                        'type_str' : 'int',
                        'val' : '2'
                    },
                    'z' : {
                        'type_str' : 'int',
                        'val' : '3'
                    },
                },
                'locals' : {
                    'x' : {
                        'type_str' : 'int',
                        'val' : '1'
                    },
                    'y' : {
                        'type_str' : 'int',
                        'val' : '2'
                    },
                    'z' : {
                        'type_str' : 'int',
                        'val' : '3'
                    },
                },
            },
            'output' : '',
            'error' : '',
        }]

        self.engine.run(simple_code_snippet, [])

        for dataset in self.engine.get_bare_language_data():
            for var, val in dataset['scenes']['globals'].items():
                del val['id']

            for var, val in dataset['scenes']['locals'].items():
                del val['id']

        self.assertEqual(self.engine.get_bare_language_data(), simple_code_data)

        conditional_code_snippet = 'if True:\n\tx = 1\nelse:\n\tx = 2\ny = 3'
        conditional_code_flags = [4]
        conditional_code_data = [{
            'scenes' : {
                'globals' : {
                    'x' : {
                        'type_str' : 'int',
                        'val' : '1'
                    },
                    'y' : {
                        'type_str' : 'int',
                        'val' : '3'
                    },
                },
                'locals' : {
                    'x' : {
                        'type_str' : 'int',
                        'val' : '1'
                    },
                    'y' : {
                        'type_str' : 'int',
                        'val' : '3'
                    },
                },
            },
            'output' : '',
            'error' : '',
        },
        {
            'scenes' : {
                'globals' : {
                    'x' : {
                        'type_str' : 'int',
                        'val' : '1'
                    },
                    'y' : {
                        'type_str' : 'int',
                        'val' : '3'
                    },
                },
                'locals' : {
                    'x' : {
                        'type_str' : 'int',
                        'val' : '1'
                    },
                    'y' : {
                        'type_str' : 'int',
                        'val' : '3'
                    },
                },
            },
            'output' : '',
            'error' : '',
        }]

        self.engine.run(conditional_code_snippet, conditional_code_flags)

        for dataset in self.engine.get_bare_language_data():
            for var, val in dataset['scenes']['globals'].items():
                del val['id']

            for var, val in dataset['scenes']['locals'].items():
                del val['id']

        self.assertEqual(self.engine.get_bare_language_data(), conditional_code_data)

        loop_code_snippet = 'for i in range(3):\n\tpass'
        loop_code_flags = [1]
        loop_code_data = [{
            'scenes' : {
                'globals' : {
                    'i' : {
                        'type_str' : 'int',
                        'val' : '0'
                    },
                },
                'locals' : {
                    'i' : {
                        'type_str' : 'int',
                        'val' : '0'
                    },
                },
            },
            'output' : '',
            'error' : '',
        },
        {
            'scenes' : {
                'globals' : {
                    'i' : {
                        'type_str' : 'int',
                        'val' : '1'
                    },
                },
                'locals' : {
                    'i' : {
                        'type_str' : 'int',
                        'val' : '1'
                    },
                },
            },
            'output' : '',
            'error' : '',
        },
        {
            'scenes' : {
                'globals' : {
                    'i' : {
                        'type_str' : 'int',
                        'val' : '2'
                    },
                },
                'locals' : {
                    'i' : {
                        'type_str' : 'int',
                        'val' : '2'
                    },
                },
            },
            'output' : '',
            'error' : '',
        },
        {
            'scenes' : {
                'globals' : {
                    'i' : {
                        'type_str' : 'int',
                        'val' : '2'
                    },
                },
                'locals' : {
                    'i' : {
                        'type_str' : 'int',
                        'val' : '2'
                    },
                },
            },
            'output' : '',
            'error' : '',
        }]

        self.engine.run(loop_code_snippet, loop_code_flags)

        for dataset in self.engine.get_bare_language_data():
            for var, val in dataset['scenes']['globals'].items():
                del val['id']

            for var, val in dataset['scenes']['locals'].items():
                del val['id']

        self.assertEqual(self.engine.get_bare_language_data(), loop_code_data)

    def test_code_execution_blacklisted_value(self):
        code = 'oops = input("this shouldnt work")'
        self.engine.run(code, []) # no flags needed for error
        self.assertEqual(self.engine.get_bare_language_data()[0]['error'].split(':')[0], "RestrictionError")

        code = 'oops = open("illegal.txt")'
        self.engine.run(code, [])
        self.assertEqual(self.engine.get_bare_language_data()[0]['error'].split(':')[0], "RestrictionError")

        code = 'oops = exec("nope nope nope")'
        self.engine.run(code, [])
        self.assertEqual(self.engine.get_bare_language_data()[0]['error'].split(':')[0], "RestrictionError")

        code = 'oops = eval("a = 5")'
        self.engine.run(code, [])
        self.assertEqual(self.engine.get_bare_language_data()[0]['error'].split(':')[0], "RestrictionError")

    def test_output_generation(self):
        self.engine.run('print(5)\nprint("hello, world")\nprint(True)', [2])

        bare_lang_data = self.engine.get_bare_language_data()
        self.assertEqual(bare_lang_data[0]['output'], '5\nhello, world\nTrue\n')


    def test_error_output_generation(self):
        self.engine.run('raise ValueError("hello")', [0])

        bare_lang_data = self.engine.get_bare_language_data()
        self.assertEqual(bare_lang_data[0]['error'], 'ValueError: hello\n')

    def test_nonglobal_namespace_code_execution(self):
        self.engine.run('g = 3\ndef f():\n\tx = 1\n\ty=2\nf()', [3])

        bare_lang_data = self.engine.get_bare_language_data()

        for snapshot in bare_lang_data:
            for scene in snapshot['scenes'].values():
                for value in scene.values():
                    del value['id']

                    if value['type_str'] == 'function':
                        value['val'] = '...'

        self.assertEqual(len(bare_lang_data), 2)
        self.assertEqual(bare_lang_data[0], {
            'scenes' : {
                'globals' : {
                    'g' : {
                        'type_str' : 'int',
                        'val' : '3',
                    },
                    'f' : {
                        'type_str' : 'function',
                        'val' : '...',
                    }
                },
                'locals' : {
                    'x' : {
                        'type_str' : 'int',
                        'val' : '1',
                    },
                    'y' : {
                        'type_str' : 'int',
                        'val' : '2',
                    },
                },
            },
            'output' : '',
            'error' : '',
        })


if __name__ == '__main__':
    vrb = 2

    if len(sys.argv) == 2:
        if re.match('^[0-9]+$', sys.argv[1]):
            vrb = int(sys.argv[1])

    unittest.main(argv=sys.argv[:1], verbosity=vrb)
