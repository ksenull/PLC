def time_this(val):
    def other_function(original_function):
        def new_function(*args,**kwargs):
            x = original_function()
            return x + val
        return new_function

    return other_function


@time_this(5)
def func_a():
    return 3

#print(func_a())


def log(clazz):
    class wrapper(object):
        def __init__(self):
            print("acessing __init__()")
            self.instance = clazz()
        def __getattribute__(self, name):
            try:
                return object.__getattribute__(self, name)
            except:
                pass
            print("Accesing " + name)
            return self.instance.__getattribute__(name)


    return wrapper

@log
class Bar:
    def __init__(self):
        self.x = 5
    def foo(self):
        print("asd")

b = Bar()
b.foo()