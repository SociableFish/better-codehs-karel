import typing

def index(n: typing.SupportsIndex, /) -> int:
    """Converts n to an integer."""
    if not isinstance(n, typing.SupportsIndex):
        raise TypeError(f"{n!r} must be a int")
    return range(n).stop

def multi_setattr[T](
        obj: T,
        setattr_fn: typing.Callable[[T, str, object], object],
        /,
        **attrs: object
) -> None:
    """Sets multiple object attributes at once."""
    for name, value in attrs.items():
        setattr_fn(obj, name, value)

def true_final[T](t: type[T], /) -> type[T]:
    def __init_subclass__(*_, **__) -> typing.Never:
        raise TypeError(f"Cannot derive from {t.__name__}")
    t.__init_subclass__ = __init_subclass__
    return t

def typefilt[T](o: T, ty: type[T], /) -> T:
    if not isinstance(o, ty):
        raise TypeError(f"{o!r} must be a {ty.__name__}")
    return o
