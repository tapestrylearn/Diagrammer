class A:
    pass

a = A()

print(A.__dict__['a'])
print(A.__dict__)
print(a.__dict__)
print(id(A.__dict__), id(a.__dict__))
