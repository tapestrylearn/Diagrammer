class SceneObject:
    pass

class CodeObject:
    pass

class BasicShape(SceneObject):
    def __init__(self, width: float, height: float, header: str, content: str):
        SceneObject.__init__(self)
        self._width = width
        self._height = height
        self._header = header
        self._content = content
        self._x = 0
        self._y = 0

    def set_x(self, x: float) -> None:
        self._x = x

    def set_y(self, y: float) -> None:
        self._y = y

    def get_width(self) -> float:
        return self._width

    def get_height(self) -> float:
        return self._height

    def get_header(self) -> str:
        return self._header

    def get_content(self) -> str:
        return self._content

    def get_x(self) -> float:
        return self._x

    def get_y(self) -> float:
        return self._y\

class Variable(BasicShape):
    SIZE = 50

    def __init__(self, name: str, typestr: str, header_gen: lambda, valuestr: str, content_gen = (lambda valuestr: valuestr)):
        BasicShape(Variable.SIZE, Variable.SIZE, header_gen(name, typestr), content_gen(valuestr))

class Value(BasicShape, CodeObject):
    RADIUS = 25

    def __init__(self, typestr: str, valuestr: str):
        BasicShape.__init__(self, Value.RADIUS * 2, Value.RADIUS * 2, typestr, valuestr)
        CodeObject.__init__(self)

class Pointer(SceneObject):
    def __init__(self, variable: Variable, codeobj: CodeObject):
        self._variable = Variable
        self._codeobj = codeobj
        self._headx = 0
        self._heady = 0
        self._tailx = 0
        self._taily = 0

    def set_headx(self, headx: float) -> None:
        self._headx = headx

    def set_heady(self, heady: float) -> None:
        self._heady = heady

    def set_tailx(self, tailx: float) -> None:
        self._tailx = tailx

    def set_taily(self, taily: float) -> None:
        self._taily = taily

    def get_variable(self) -> Variable:
        return self._variable

    def get_codeobj(self) -> CodeObject:
        return self._codeobj

    def get_headx(self) -> float:
        return self._headx

    def get_heady(self) -> float:
        return self._heady

    def get_tailx(self) -> float:
        return self._tailx

    def get_taily(self) -> float:
        return self._taily
