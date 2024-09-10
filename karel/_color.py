import ast
import dataclasses
import itertools
import typing
from typing import SupportsIndex as Int

from . import _helpers

def all_hex_digits(*ss: str) -> bool:
    return all(i in "0123456789abcdefABCDEF" for i in itertools.chain(ss))

color: dict[str, "RGB"]

@_helpers.true_final
@typing.final
@dataclasses.dataclass(init=False, frozen=True, slots=True)
class RGB:
    """An immutable `dataclass` that stores a color in RGB using `.r`, `.g`,
and `.b`. Construct using `RGB(r, g, b)` or `RGB(r=r, g=g, b=b)` to create the
color with `.r == r`, `.g == g`, and `.b == b`. Constructor raises `TypeError`
for non-`int` arguments and `ValueError` for arguments not in `range(256)`.
`__str__` outputs hex color notation (#rrggbb), use `repr()` for decimal
channels."""
    r: int
    g: int
    b: int

    def __new__(cls, r: Int, g: Int, b: Int) -> "RGB":
        self = super(cls, cls).__new__(cls) # type: ignore
        r = _helpers.index(r)
        g = _helpers.index(g)
        b = _helpers.index(b)
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise ValueError("Color values not in range 0-255")
        _helpers.multi_setattr(self, object.__setattr__, r=r, g=g, b=b)
        return self

    def __str__(self) -> str:
        """`__str__` outputs hex color notation (#rrggbb), use `repr()` for
decimal channels."""
        return f"#{self.r:0>2x}{self.g:0>2x}{self.b:0>2x}"
    
    @staticmethod
    def from_str(c: "str | RGB", /) -> "RGB":
        """If `c` is an `RGB`, returns `c`. If `c` is not a `str` or `RGB`,
raises a `TypeError`. Otherwise, first runs `c = c.lower()`. If `c` is a
predefined color name in `color`, outputs its corresponding `RGB`. Otherwise,
if `c` is of the form `"#ghi"`, returns `RGB(0xgg, 0xhh, 0xii)`. Otherwise, if
`c` is of the form `"#ghijkl"`, returns `RGB(0xgh, 0xij, 0xkl)`. Otherwise, if
`c` is of the form `"rgb(c, d, e)"` or `"rgb(r=c, g=d, b=e)"`, returns
`RGB(c, d, e)`. Otherwise, raises a `ValueError`."""
        if isinstance(c, RGB):
            return c
        if not isinstance(c, str):
            raise TypeError(f"{c!r} must be a str or RGB")  
        c = c.lower()
        if c in color:
            return _helpers.typefilt(color[c], RGB)
        match list(c):
            case ['#', r, g, b] if all_hex_digits(r, g, b):
                return RGB(int(r * 2, 16), int(g * 2, 16), int(b * 2, 16))
            case ['#', r1, r2, g1, g2, b1, b2] \
            if all_hex_digits(r1, r2, g1, g2, b1, b2):
                return RGB(
                    int(r1 + r2, 16),
                    int(g1 + g2, 16),
                    int(b1 + b2, 16)
                )
        try:
            match ast.parse(c, mode="eval"):
                case ast.Expression(
                    body=ast.Call(
                        func=ast.Name(id="rgb"),
                        args=[
                            ast.Constant(value=r),
                            ast.Constant(value=g),
                            ast.Constant(value=b)
                        ],
                        keywords=[]
                    ) | ast.Call(
                        func=ast.Name(id="rgb"),
                        args=[],
                        keywords=[
                            ast.keyword(arg="r", value=ast.Constant(value=r)),
                            ast.keyword(arg="g", value=ast.Constant(value=g)),
                            ast.keyword(arg="b", value=ast.Constant(value=b))
                        ]
                    )
                ) if (
                        isinstance(r, typing.SupportsIndex)
                    and isinstance(g, typing.SupportsIndex)
                    and isinstance(b, typing.SupportsIndex)
                ):
                    return RGB(r, g, b)
        except SyntaxError:
            pass
        raise ValueError(f"{c!r} is not a valid color string")

color = {
    "red":    RGB(255,   0,   0),
    "green":  RGB(  0, 255,   0),
    "blue":   RGB(  0,   0, 255),
    "yellow": RGB(255, 255,   0),
    "cyan":   RGB(  0, 255, 255),
    "orange": RGB(255, 165,   0),
    "white":  RGB(255, 255, 255),
    "black":  RGB(  0,   0,   0),
    "gray":   RGB(204, 204, 204),
    "purple": RGB(155,  48, 255),
}
"""The color dictionary used to map color names to colors. By default, uses the
10 names listed in the CodeHS "Docs" tab and the colors emitted by CodeHS as
keys and values, respectively. Since this object is mutable, name-color
mappings can be freely added and removed."""