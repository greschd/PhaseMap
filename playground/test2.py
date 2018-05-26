#!/usr/bin/env python

from phasemap import run

run(lambda x: len(x), limits=[(-1, 1)])
