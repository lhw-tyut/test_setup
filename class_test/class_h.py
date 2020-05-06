class A():
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def executor(self):
        print("aaa")

    def output(self):
        self.executor()


class B(A):

    def executor(self):
        print("bbb")

    def output(self):
        self.executor()


a = A(1, 2)
a.output()
b = B(1, 2)
b.output()