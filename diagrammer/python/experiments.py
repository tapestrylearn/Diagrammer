import model

def make_models(this_locals: {str : object}) -> (dict, dict):
    objs = {name : model.PyObject.make_for_obj(obj) for name, obj in this_locals.items() if name != 'self'}
    vars = {name : model.Variable(name, obj) for name, obj in objs.items()}
    return (objs, vars)

def test():
    class A():
        pass

    a = A()
    a.my_copy = a
    a.my_namespace = a.__dict__

    objs, _ = make_models(locals())

test()
