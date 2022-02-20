"""Provides some utilities widely used by other modules"""

import functools

def print_debugger(function):
    
    @functools.wraps(function)
    def result(*args, **kwargs):

        debugName = function.__name__ + "("
        if args:
            for i, arg in enumerate(args):
                if i != 0:
                    debugName += ", "
                debugName += repr(arg)
        if kwargs:
            for i, (arg, val) in enumerate(kwargs.items()):
                if i != 0 or len(args) > 0:
                    debugName += ", "
                debugName += str(arg) + "=" + str(val)
        debugName += ")"
        print(f"C {debugName}")
        res = function(*args, **kwargs)
        if res:
            print(f"R {debugName} = {res}")
        return res
    return result

