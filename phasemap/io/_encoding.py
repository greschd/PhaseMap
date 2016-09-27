#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.04.2016 10:21:56 CEST
# File:    _encoding.py

import numbers
import contextlib
from functools import singledispatch
from collections.abc import Iterable

import numpy as np
from fsc.export import export

from .._container import PhaseMap, Square, Point, StepDict

@export
@singledispatch
def encode(obj):
    """
    Encodes Z2Pack types into JSON / msgpack - compatible types.
    """
    raise TypeError('cannot JSONify {} object {}'.format(type(obj), obj))

@encode.register(np.bool_)
def _(obj):
    return bool(obj)

@encode.register(numbers.Real)
def _(obj):
    return float(obj)

@encode.register(numbers.Complex)
def _(obj):
    return dict(__complex__=True, real=encode(obj.real), imag=encode(obj.imag))

@encode.register(Iterable)
def _(obj):
    return list(obj)

@encode.register(PhaseMap)
def _(obj):
    return dict(
        __phasemap__=True,
        limits=obj.limits,
        mesh=obj.mesh,
        points=obj.points,
        squares=obj.squares,
        all_corners=obj.all_corners,
        _to_split=obj._to_split,
        _to_calculate=obj._to_calculate,
        _split_next=obj._split_next
    )

@encode.register(StepDict)
def _(obj):
    return dict(
        __stepdict__=True,
        step=obj.step,
        data_items=sorted(obj.data.items())
    )

@encode.register(Point)
def _(obj):
    return dict(
        __point__=True,
        phase=obj.phase,
        squares=list(obj.squares)
    )

@encode.register(Square)
def _(obj):
    return dict(
        __square__=True,
        corner=obj.corner,
        phase=obj.phase,
        size=obj.size,
        points=list(obj.points)
    )

#-----------------------------------------------------------------------#

@export
@singledispatch
def decode(obj):
    """
    Decodes JSON / msgpack objects into the corresponding Z2Pack types.
    """
    return obj

def decode_complex(obj):
    return complex(obj['real'], obj['imag'])

def decode_phasemap(obj):
    res = PhaseMap(mesh=obj['mesh'], limits=obj['limits'])
    res.points = decode(obj['points'])
    res.squares = decode(obj['squares'])
    res.all_corners = obj['all_corners']
    res._to_split = obj['_to_split']
    res._to_calculate = obj['_to_calculate']
    res._split_next = obj['_split_next']
    return res

def decode_point(obj):
    res = Point(phase=obj['phase'])
    res.squares = set(obj['squares'])
    return res
    
def decode_square(obj):
    res = Square(corner=obj['corner'], size=obj['size'])
    res.phase = obj['phase']
    res.points = set([tuple(p) for p in obj['points']])
    return res
    
def decode_stepdict(obj):
    res = StepDict(step=obj['step'])
    res.data = {tuple(k): v for k, v in obj['data_items']}
    return res

@decode.register(dict)
def _(obj):
    with contextlib.suppress(AttributeError):
        obj = {k.decode('utf-8'): v for k, v in obj.items()}
    special_markers = [key for key in obj.keys() if key.startswith('__')]
    if len(special_markers) == 1:
        name = special_markers[0].strip('__')
        return globals()['decode_' + name](obj)
    else:
        return obj

