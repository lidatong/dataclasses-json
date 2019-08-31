from hypothesis import example


def examples(*args):
    """A variadic `examples` decorator to both supplant stacking of @example
    and support iterables being passed in directly
    """

    def examples_decorator(f):
        g = f
        for arg in args:
            g = example(arg)(g)
        return g

    return examples_decorator
