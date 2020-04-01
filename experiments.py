from diagrammer import model

x = [1, 2, 3]
y = [x, 2, 3]
y_model = model.PyObject.make_for_obj(y)
print(y_model.export())
