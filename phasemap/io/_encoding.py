# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

# pylint: disable=protected-access

import numbers
import contextlib
from functools import singledispatch
from collections.abc import Iterable
from fractions import Fraction

import numpy as np
from fsc.export import export

from .._box import Box, Sentinel
from .._coordinate import Coordinate
from .._result import Result


@export
@singledispatch
def encode(obj):
    """
    Encodes PhaseMap types into JSON / msgpack - compatible types.
    """
    raise TypeError("cannot JSONify {} object {}".format(type(obj), obj))


@encode.register(np.bool_)
def _encode_bool(obj):
    return bool(obj)


@encode.register(Fraction)
def _encode_fraction(obj):
    return dict(__fraction__=True, n=obj.numerator, d=obj.denominator)


@encode.register(numbers.Real)
def _encode_real(obj):
    return float(obj)


@encode.register(numbers.Complex)
def _encode_complex(obj):
    return dict(__complex__=True, real=encode(obj.real), imag=encode(obj.imag))


@encode.register(Iterable)
def _encode_iterable(obj):
    return list(obj)


@encode.register(Result)
def _encode_result(obj):
    return dict(
        __result__=True,
        points=obj.points.items(),
        boxes=obj.boxes,
        limits=obj.limits,
    )


@encode.register(Coordinate)
def _encode_coordinate(obj):
    return dict(__coord__=True, c=list(obj))


@encode.register(Box)
def _encode_box(obj):
    return dict(
        __box__=True,
        corner=obj.corner,
        phase=obj.phase,
        size=obj.size,
    )


@encode.register(Sentinel)
def _encode_sentinel(obj):
    return dict(__sentinel__=True, value=obj._value)


# -----------------------------------------------------------------------#


@export
@singledispatch
def decode(obj):
    """
    Decodes JSON / msgpack objects into the corresponding PhaseMap types.
    """
    return obj


def decode_complex(obj):
    return complex(obj["real"], obj["imag"])


def decode_result(obj):
    return Result(
        points=dict(obj["points"]),
        boxes=obj["boxes"],
        limits=obj["limits"],
    )


def decode_box(obj):
    res = Box(corner=obj["corner"], size=obj["size"])
    res.phase = obj["phase"]
    return res


def decode_coord(obj):
    return Coordinate(obj["c"])


def decode_fraction(obj):
    return Fraction(obj["n"], obj["d"])


def decode_sentinel(obj):
    return Sentinel(obj["value"])


@decode.register(dict)
def _(obj):
    with contextlib.suppress(AttributeError):
        obj = {k.decode("utf-8"): v for k, v in obj.items()}
    special_markers = [key for key in obj.keys() if key.startswith("__")]
    if len(special_markers) == 1:
        name = special_markers[0].strip("__")
        return globals()["decode_" + name](obj)
    else:
        return obj
