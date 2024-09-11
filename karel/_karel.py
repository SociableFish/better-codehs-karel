import copy
from collections.abc import Iterable as _Iterable
from collections.abc import Sequence as _Sequence
from collections.abc import Sized as _Sized
import dataclasses
import enum
import itertools
import pathlib
import types
import typing
from typing import SupportsIndex as _Int

from ._color import color, RGB
from . import _helpers

def _2d_arr_size(arr: _Sequence[_Sized], /) -> tuple[int, int | None]:
    isize: int = len(arr)
    jsize: int | None = None
    for idx, length in enumerate(map(len, arr)):
        if jsize is None:
            jsize = length
        elif jsize != length:
            raise ValueError(f"{arr!r} is not a valid 2D array")
    return (isize, jsize)

def _ensure_size(
        arr: _Sequence[_Sized],
        isize: int,
        jsize: int,
        name: str,
        /
) -> None:
    arr_isize = len(arr)
    if arr_isize != isize:
        raise ValueError(
            f"Expected {isize} elements in {name}, found {arr_isize}"
            f" (note: {name}={arr!r})"
        )
    for idx, length in enumerate(map(len, arr)):
        if length != jsize:
            raise ValueError(
                f"Expected {jsize} elements in {name}[{idx}], found {length}"
                f" (note: {name}={arr!r})"
            )
        arr_isize += 1

@typing.final
class Direction(enum.StrEnum):
    """An `enum.StrEnum` that stores Karel's direction. 4 alternatives:
`Direction.north`, `Direction.south`, `Direction.east`, `Direction.west`.
`.turned_left`, `.turned_right`, `.turned_around` are all properties that
return a direction that is turned as specified in the property name."""
    north = "north"
    south = "south"
    east =  "east"
    west =  "west"

    def __repr__(self) -> str:
        return f"Direction.{str(self)}"

    @property
    def turned_left(self) -> "Direction":
        match self:
            case Direction.north:
                return Direction.west
            case Direction.south:
                return Direction.east
            case Direction.east:
                return Direction.north
            case Direction.west:
                return Direction.south
    
    @property
    def turned_right(self) -> "Direction":
        match self:
            case Direction.north:
                return Direction.east
            case Direction.south:
                return Direction.west
            case Direction.east:
                return Direction.south
            case Direction.west:
                return Direction.north
    
    @property
    def turned_around(self) -> "Direction":
        match self:
            case Direction.north:
                return Direction.south
            case Direction.south:
                return Direction.north
            case Direction.east:
                return Direction.west
            case Direction.west:
                return Direction.east

@typing.final
@dataclasses.dataclass(init=False, frozen=True, slots=True)
class AvenueAndStreet:
    """An immutable `dataclass` that stores a position in a Karel world using
`.avenue` (X position) and `.street` (Y position). Construct using
`AvenueAndStreet(avenue, street)` or
`AvenueAndStreet(avenue=avenue, street=street)` to create the position with
`.avenue == avenue` and `.street == street`. Constructor raises `TypeError` for
non-`int` arguments and `ValueError` for negative arguments. `.with_avenue()`
and `.with_street()` each return an `AvenueAndStreet` with specified avenue and
street and the other property taken from the object whose instance is called.
`.moved()` takes in a `Direction` and returns a new `AvenueAndStreet` moved by
1 in that direction. (north = +Y, south = -Y, east = +X, west = -X)"""
    avenue: int
    street: int

    def __new__(cls, avenue: _Int, street: _Int) -> "AvenueAndStreet":
        self = super(cls, cls).__new__(cls)
        avenue = _helpers.index(avenue)
        street = _helpers.index(street)
        if avenue < 0 or street < 0:
            raise ValueError(
                "Avenue and street must both be non-negative "
                f"(avenue={avenue}, street={street})"
            )
        _helpers.multi_setattr(
            self,
            object.__setattr__,
            avenue=avenue,
            street=street
        )
        return self
    
    def with_avenue(self, avenue: _Int, /) -> "AvenueAndStreet":
        return AvenueAndStreet(avenue, self.street)
    
    def with_street(self, street: _Int, /) -> "AvenueAndStreet":
        return AvenueAndStreet(self.avenue, street)
    
    def moved(self, direction: Direction, /) -> "AvenueAndStreet":
        match direction:
            case Direction.north:
                return self.with_street(self.street + 1)
            case Direction.south:
                return self.with_street(self.street - 1)
            case Direction.east:
                return self.with_avenue(self.avenue + 1)
            case Direction.west:
                return self.with_avenue(self.avenue - 1)
    
    def _in_bounds(self, position: "AvenueAndStreet", /) -> bool:
        position = _helpers.typefilt(position, AvenueAndStreet)
        return position.avenue < self.avenue and position.street < self.street

@_helpers.true_final
@typing.final
@dataclasses.dataclass(init=False, frozen=True, slots=True)
class Karel:
    """An immutable `dataclass` that stores the position and direction of a
Karel in a Karel world using `.position` and `.direction`. Construct using
`Karel(position, direction)` or `Karel(position=position, direction=direction)`
to create the `Karel` with `.position == position` and
`.direction == direction` Constructor raises `TypeError` if `position` is not
an `AvenueAndStreet` or if `direction` is not a `Direction` `.facing_north`,
`.facing_south`, `.facing_east`, and `.facing_west` are all properties that
return if `.direction` equals a certain `Direction`. `self.moved_to(position)`
is just `Karel(position, self.direction)`. `self.with_avenue(avenue)` is just
`self.moved_to(self.position.with_avenue(avenue))`. `self.with_street(street)`
is just `self.moved_to(self.position.with_street(street))`. `self.moved` is a
property that just returns `self.moved_to(self.position.moved)`.
`self.turned(direction)` is just `Karel(self.position, direction)`.
`.turned_left`, `.turned_right`, and `.turned_around` are just properties that
return for a given `self` `self.turned(self.direction.<property>)`.
"""
    position: AvenueAndStreet
    direction: Direction

    def __new__(
            cls,
            position: AvenueAndStreet,
            direction: Direction = Direction.east
    ) -> "Karel":
        self = super(cls, cls).__new__(cls)
        _helpers.multi_setattr(
            self,
            object.__setattr__,
            position=_helpers.typefilt(position, AvenueAndStreet),
            direction=_helpers.typefilt(direction, Direction)
        )
        return self
    
    @property
    def facing_north(self) -> bool:
        return self.direction == Direction.north
    
    @property
    def facing_south(self) -> bool:
        return self.direction == Direction.south
    
    @property
    def facing_east(self) -> bool:
        return self.direction == Direction.east
    
    @property
    def facing_west(self) -> bool:
        return self.direction == Direction.west
    
    def moved_to(self, position: AvenueAndStreet, /) -> "Karel":
        return Karel(position, self.direction)
    
    def with_avenue(self, avenue: _Int, /) -> "Karel":
        return self.moved_to(self.position.with_avenue(avenue))
    
    def with_street(self, street: _Int, /) -> "Karel":
        return self.moved_to(self.position.with_street(street))
    
    @property
    def moved(self) -> "Karel":
        return self.moved_to(self.position.moved(self.direction))
    
    def turned(self, direction: Direction, /) -> "Karel":
        return Karel(self.position, direction)
    
    @property
    def turned_left(self) -> "Karel":
        return self.turned(self.direction.turned_left)
    
    @property
    def turned_right(self) -> "Karel":
        return self.turned(self.direction.turned_right)
    
    @property
    def turned_around(self) -> "Karel":
        return self.turned(self.direction.turned_around)

@_helpers.true_final
@typing.final
@dataclasses.dataclass(init=False, repr=False, match_args=False, slots=True)
class World:
    """Class that stores the state of an Ultra Karel world. Super Karel is just
Ultra Karel without randomness or color support, and Normal Karel is just Super
Karel without `turn_right` or `turn_around`. See method docstrings of
`.globals()` and `.exec_from()` for more info."""
    _karel: Karel
    _ball_counts: list[list[int]]
    _horizontal_walls: list[list[bool]]
    _vertical_walls: list[list[bool]]
    _colors: list[list[RGB]]

    def __init__(
            self,
            *,
            karel: Karel = Karel(AvenueAndStreet(0, 0)),
            ball_counts: _Iterable[_Iterable[_Int]],
            horizontal_walls: _Iterable[_Iterable[bool]] | None = None,
            vertical_walls: _Iterable[_Iterable[bool]] | None = None,
            colors: _Iterable[_Iterable[str | RGB]] | None = None
    ) -> None:
        self._karel = _helpers.typefilt(karel, Karel)

        self._ball_counts = [
            [_helpers.index(j) for j in _helpers.typefilt(i, _Iterable)]
            for i in _helpers.typefilt(ball_counts, _Iterable)
        ]
        isize, jsize = _2d_arr_size(self._ball_counts)
        if isize == 0 or jsize == 0 or jsize is None:
            raise ValueError(f"{ball_counts!r} is an empty 2D array")
        
        if horizontal_walls is None:
            horizontal_walls = (
                (False for _ in range(jsize)) for _ in range(isize - 1)
            )
        self._horizontal_walls = [
            [bool(j) for j in _helpers.typefilt(i, _Iterable)]
            for i in _helpers.typefilt(horizontal_walls, _Iterable)
        ]
        _ensure_size(
            self._horizontal_walls,
            isize - 1,
            jsize,
            "horizontal_walls"
        )

        if vertical_walls is None:
            vertical_walls = (
                (False for _ in range(jsize - 1)) for _ in range(isize)
            )
        self._vertical_walls = [
            [bool(j) for j in _helpers.typefilt(i, _Iterable)]
            for i in _helpers.typefilt(vertical_walls, _Iterable)
        ]
        _ensure_size(
            self._horizontal_walls,
            isize,
            jsize - 1,
            "vertical_walls"
        )
        
        if colors is None:
            colors = (("white" for _ in range(jsize)) for _ in range(isize))
        self._colors = [
            [RGB.from_str(j) for j in _helpers.typefilt(i, _Iterable)]
            for i in _helpers.typefilt(colors, _Iterable)
        ]
        _ensure_size(self._horizontal_walls, isize, jsize, "colors")
        
        if not self.size._in_bounds(karel.position):
            raise ValueError(
                "Invalid Karel position "
                f"(position={karel.position}, size={self.size})"
            )

    @staticmethod
    def empty_world_with_size(
            size: AvenueAndStreet,
            karel: Karel = Karel(AvenueAndStreet(0, 0)),
            /
    ) -> "World":
        size = _helpers.typefilt(size, AvenueAndStreet)
        return World(
            karel=karel,
            ball_counts=(
                (0 for _ in range(size.avenue))
                for _ in range(size.street)
            )
        )

    def __repr__(self) -> str:
        return "World(" \
            f"karel={self.karel}, " \
            f"ball_counts={self._ball_counts}, " \
            f"horizontal_walls={self._horizontal_walls}, " \
            f"vertical_walls={self._vertical_walls}, " \
            f"colors={self._colors}" \
        ")"
    
    @property
    def size(self) -> AvenueAndStreet:
        return AvenueAndStreet(
            len(self._ball_counts[0]), len(self._ball_counts)
        )
    @size.setter
    def size(self, new: AvenueAndStreet, /) -> None:
        new = _helpers.typefilt(new, AvenueAndStreet)
        if new.street == 0 or new.avenue == 0:
            raise ValueError(
                f"New size cannot have 0 as a dimension (new size = {new})"
            )
        if not new._in_bounds(self.karel.position):
            raise ValueError(
                "Karel would be out of bounds "
                f"(his position = {self.karel.position}, new size = {new})"
            )
        if new.street < self.size.street:
            to_delete: int = self.size.street - new.street
            del self._ball_counts[:to_delete]
            del self._horizontal_walls[:to_delete]
            del self._vertical_walls[:to_delete]
            del self._colors[:to_delete]
        if new.street > self.size.street:
            to_add: int = new.street - self.size.street
            self._ball_counts[:0] = (
                [0] * self.size.avenue for _ in range(to_add)
            )
            self._horizontal_walls[:0] = (
                [False] * self.size.avenue for _ in range(to_add)
            )
            self._vertical_walls[:0] = (
                [False] * (self.size.avenue - 1) for _ in range(to_add)
            )
            self._colors[:0] = (
                [RGB(255, 255, 255)] * self.size.avenue for _ in range(to_add)
            )
        if new.avenue < self.size.avenue:
            to_delete: int = self.size.avenue - new.avenue
            for i in itertools.chain(
                self._ball_counts,
                self._horizontal_walls,
                self._vertical_walls,
                self._colors
            ):
                del i[-to_delete:]
        if new.avenue > self.size.avenue:
            to_add: int = new.avenue - self.size.avenue
            for i in self._ball_counts:
                i.extend(0 for _ in range(to_add))
            for i in itertools.chain(
                self._horizontal_walls,
                self._vertical_walls
            ):
                i.extend(False for _ in range(to_add))
            for i in self._colors:
                i.extend(RGB(255, 255, 255) for _ in range(to_add))
    
    def _list_index(self, position: AvenueAndStreet, /) -> tuple[int, int]:
        position = _helpers.typefilt(position, AvenueAndStreet)
        return (self.size.street - position.street - 1, position.avenue)
    
    @property
    def karel(self) -> Karel:
        return self._karel
    @karel.setter
    def karel(self, new: Karel, /) -> None:
        position = _helpers.typefilt(new, Karel).position
        if not self.size._in_bounds(position):
            raise ValueError(
                f"Karel's new position ({position}) out of range "
                f"(size={self.size})"
            )
        self._karel = new
    
    @property
    def ball_counts(self) -> list[list[int]]:
        return copy.deepcopy(self._ball_counts)
    @ball_counts.setter
    def ball_counts(self, new: _Iterable[_Iterable[_Int]] | None, /) -> None:
        if new is None:
            self._ball_counts = [
                [0 for _ in range(self.size.street)]
                for _ in range(self.size.avenue)
            ]
            return
        new = [
            [_helpers.index(j) for j in _helpers.typefilt(i, _Iterable)]
            for i in _helpers.typefilt(new, _Iterable)
        ]
        isize, jsize = _2d_arr_size(new)
        if isize == 0 or jsize == 0 or jsize is None:
            raise ValueError(f"{new!r} is an empty 2D array")
        self.size = AvenueAndStreet(jsize, isize)
        self._ball_counts = new

    @property
    def horizontal_walls(self) -> list[list[bool]]:
        return copy.deepcopy(self._horizontal_walls)
    @horizontal_walls.setter
    def horizontal_walls(
            self,
            new: _Iterable[_Iterable[bool]] | None,
            /
    ) -> None:
        if new is None:
            self._horizontal_walls = [
                [False for _ in range(self.size.street)]
                for _ in range(self.size.avenue - 1)
            ]
            return
        new = [
            [
                _helpers.typefilt(j, bool)
                for j in _helpers.typefilt(i, _Iterable)
            ]
            for i in _helpers.typefilt(new, _Iterable)
        ]
        isize, jsize = _2d_arr_size(new)
        if isize == 0 or jsize is None:
            jsize = self.size.avenue
        self.size = AvenueAndStreet(jsize, isize + 1)
        self._horizontal_walls = new

    @property
    def vertical_walls(self) -> list[list[bool]]:
        return copy.deepcopy(self._vertical_walls)
    @vertical_walls.setter
    def vertical_walls(
            self,
            new: _Iterable[_Iterable[bool]] | None,
            /
    ) -> None:
        if new is None:
            self._vertical_walls = [
                [False for _ in range(self.size.street - 1)]
                for _ in range(self.size.avenue)
            ]
            return
        new = [
            [
                _helpers.typefilt(j, bool)
                for j in _helpers.typefilt(i, _Iterable)
            ]
            for i in _helpers.typefilt(new, _Iterable)
        ]
        isize, jsize = _2d_arr_size(new)
        if isize == 0 or jsize is None:
            raise ValueError(
                f"{new!r} is an invalid empty 2D array for vertical walls"
            )
        self.size = AvenueAndStreet(jsize + 1, isize)
        self._vertical_walls = new

    @property
    def colors(self) -> list[list[RGB]]:
        return copy.deepcopy(self._colors)
    @colors.setter
    def colors(self, new: _Iterable[_Iterable[str | RGB]]| None, /) -> None:
        if new is None:
            self._colors = [
                [RGB(255, 255, 255) for _ in range(self.size.street)]
                for _ in range(self.size.avenue)
            ]
            return
        new = [
            [RGB.from_str(j) for j in _helpers.typefilt(i, _Iterable)]
            for i in _helpers.typefilt(new, _Iterable)
        ]
        isize, jsize = _2d_arr_size(new)
        if isize == 0 or jsize == 0 or jsize is None:
            raise ValueError(f"{new!r} is an empty 2D array")
        self.size = AvenueAndStreet(jsize, isize)
        self._colors = new
    
    def copy(self) -> "World":
        return World(
            karel=self.karel,
            ball_counts=self._ball_counts,
            horizontal_walls=self._horizontal_walls,
            vertical_walls=self._vertical_walls,
            colors=self._colors
        )
    
    __copy__ = copy
    
    def __deepcopy__(self, _) -> "World":
        return self.copy()
    
    def move_karel(self, position: AvenueAndStreet, /) -> None:
        self.karel = Karel(position, self.karel.direction)
    
    def rotate_karel(self, direction: Direction, /) -> None:
        self.karel = Karel(self.karel.position, direction)
    
    def ball_count(self, position: AvenueAndStreet | None = None, /) -> int:
        if position is None:
            position = self.karel.position
        if not self.size._in_bounds(position):
            raise IndexError(f"Position to query ({position}) out of range")
        i, j = self._list_index(position)
        return self._ball_counts[i][j]
    
    def set_ball_count(
            self,
            new: _Int,
            position: AvenueAndStreet | None = None,
            /
    ) -> None:
        if position is None:
            position = self.karel.position
        if not self.size._in_bounds(position):
            raise IndexError(f"Position to set ({position}) out of range")
        new = _helpers.index(new)
        if new < 0:
            raise ValueError(f"Tried to put {new} balls at {position}")
        i, j = self._list_index(position)
        self._ball_counts[i][j] = new
    
    def color_at(self, position: AvenueAndStreet | None = None, /) -> RGB:
        if position is None:
            position = self.karel.position
        if not self.size._in_bounds(position):
            raise IndexError(f"Position to query ({position}) out of range")
        i, j = self._list_index(position)
        return self._colors[i][j]

    def paint(
            self,
            new: RGB,
            position: AvenueAndStreet | None = None,
            /
    ) -> None:
        if position is None:
            position = self.karel.position
        if not self.size._in_bounds(position):
            raise IndexError(f"Position to set ({position}) out of range")
        i, j = self._list_index(position)
        self._colors[i][j] = _helpers.typefilt(new, RGB)
    
    def is_blocked(
            self,
            *,
            position: AvenueAndStreet | None = None,
            direction: Direction | None = None
    ) -> bool:
        if position is None:
            position = self.karel.position
        if direction is None:
            direction = self.karel.direction
        if not self.size._in_bounds(position):
            raise IndexError(f"Position to query ({position}) out of range")
        i, j = self._list_index(position)
        direction = _helpers.typefilt(direction, Direction)
        if direction == Direction.north:
            i -= 1
            direction = Direction.south
        if direction == Direction.south:
            if not (0 <= i < self.size.street - 1):
                return True
            return self._horizontal_walls[i][j]
        if direction == Direction.west:
            j -= 1
            direction = Direction.east
        if direction == Direction.east:
            if not (0 <= j < self.size.avenue - 1):
                return True
            return self._vertical_walls[i][j]
    
    def is_clear(
            self,
            *,
            position: AvenueAndStreet | None = None,
            direction: Direction | None = None
    ) -> bool:
        return not self.is_blocked(position=position, direction=direction)
    
    def set_is_blocked(
            self,
            wall: bool,
            /,
            *,
            position: AvenueAndStreet | None = None,
            direction: Direction | None = None,
    ) -> None:
        if position is None:
            position = self.karel.position
        if direction is None:
            direction = self.karel.direction
        if not self.size._in_bounds(position):
            raise IndexError(f"Position to set ({position}) out of range")
        i, j = self._list_index(position)
        direction = _helpers.typefilt(direction, Direction)
        if direction == Direction.north:
            i -= 1
            direction = Direction.south
        if direction == Direction.south:
            if not (0 <= i < self.size.street - 1):
                raise IndexError(f"Position to set ({position}) out of range")
            self._horizontal_walls[i][j] = _helpers.typefilt(wall, bool)
        if direction == Direction.west:
            j -= 1
            direction = Direction.east
        if direction == Direction.east:
            if not (0 <= j < self.size.avenue - 1):
                raise IndexError(f"Position to set ({position}) out of range")
            self._vertical_walls[i][j] = _helpers.typefilt(wall, bool)
    
    def set_is_clear(
            self,
            wall: bool,
            /,
            *,
            position: AvenueAndStreet | None = None,
            direction: Direction | None = None,
    ) -> None:
        return self.set_is_blocked(
            not _helpers.typefilt(wall, bool),
            position=position,
            direction=direction
        )
    
    def turn_left(self) -> None:
        self.karel = self.karel.turned_left
    
    def turn_right(self) -> None:
        self.karel = self.karel.turned_right
    
    def turn_around(self) -> None:
        self.karel = self.karel.turned_around
    
    def put_ball(self, position: AvenueAndStreet | None = None, /) -> None:
        if position is None:
            position = self.karel.position
        self.set_ball_count(self.ball_count(position) + 1, position)
    
    def take_ball(self, position: AvenueAndStreet | None = None, /) -> None:
        if position is None:
            position = self.karel.position
        self.set_ball_count(self.ball_count(position) - 1, position)
    
    def balls_present(
            self,
            position: AvenueAndStreet | None = None,
            /
    ) -> bool:
        if position is None:
            position = self.karel.position
        return self.ball_count(position) != 0
    
    def no_balls_present(
            self,
            position: AvenueAndStreet | None = None,
            /
    ) -> bool:
        return not self.balls_present(position)
    
    def front_is_clear(self) -> bool:
        return self.is_clear()
    
    def left_is_clear(self) -> bool:
        return self.is_clear(direction=self.karel.direction.turned_left)
    
    def right_is_clear(self) -> bool:
        return self.is_clear(direction=self.karel.direction.turned_right)
    
    def front_is_blocked(self) -> bool:
        return self.is_blocked()
    
    def left_is_blocked(self) -> bool:
        return self.is_blocked(direction=self.karel.direction.turned_left)
    
    def right_is_blocked(self) -> bool:
        return self.is_blocked(direction=self.karel.direction.turned_right)
    
    def move(self) -> None:
        if self.front_is_blocked():
            raise ValueError(f"Tried to move Karel ({self.karel}) into a wall")
        self.karel = self.karel.moved

    def facing_north(self) -> bool:
        return self.karel.facing_north
    
    def facing_south(self) -> bool:
        return self.karel.facing_south
    
    def facing_east(self) -> bool:
        return self.karel.facing_east
    
    def facing_west(self) -> bool:
        return self.karel.facing_west
    
    def not_facing_north(self) -> bool:
        return not self.facing_north()
    
    def not_facing_south(self) -> bool:
        return not self.facing_south()
    
    def not_facing_east(self) -> bool:
        return not self.facing_east()
    
    def not_facing_west(self) -> bool:
        return not self.facing_west()
    
    def color_is(self, color: str | RGB, /) -> bool:
        return self.color_at() == RGB.from_str(color)
    
    def globals(
            self,
            mode: typing.Literal["normal", "super", "ultra"],
            /
    ) -> dict[str, typing.Any]:
        mode = _helpers.typefilt(mode, str) # type: ignore
        if mode not in {"normal", "super", "ultra"}:
            raise ValueError(f"{mode!r} is not a valid mode")
        result: dict[str, typing.Any] = {
            "move": self.move,
            "turn_left": self.turn_left,
            "put_ball": self.put_ball,
            "take_ball": self.take_ball,
            "balls_present": self.balls_present,
            "no_balls_present": self.no_balls_present,
            "front_is_clear": self.front_is_clear,
            "left_is_clear": self.left_is_clear,
            "right_is_clear": self.right_is_clear,
            "front_is_blocked": self.front_is_blocked,
            "left_is_blocked": self.left_is_blocked,
            "right_is_blocked": self.right_is_blocked,
            "facing_north": self.facing_north,
            "facing_south": self.facing_south,
            "facing_east": self.facing_east,
            "facing_west": self.facing_west,
            "not_facing_north": self.not_facing_north,
            "not_facing_south": self.not_facing_south,
            "not_facing_east": self.not_facing_east,
            "not_facing_west": self.not_facing_west,
        }
        if mode in {"super", "ultra"}:
            result.update(
                turn_right=self.turn_right,
                turn_around=self.turn_around,
            )
        if mode == "ultra":
            result.update(
                color=color,
                paint=self.paint,
                color_is=self.color_is,
            )
        return result
    
    def exec_from(
            self,
            source: str | pathlib.Path | types.CodeType,
            mode: typing.Literal["normal", "super", "ultra"],
            /
    ) -> None:
        filename: str = ""
        if isinstance(source, pathlib.Path):
            filename = str(source)
            source = source.read_text(encoding="utf-8")
        if isinstance(source, str):
            source = compile(source, filename, "exec")
        exec(_helpers.typefilt(source, types.CodeType), self.globals(mode))
