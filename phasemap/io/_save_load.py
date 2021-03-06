# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import pickle

from fsc.iohelper import SerializerDispatch

from . import _encoding

__all__ = ["save", "load"]

IO_HANDLER = SerializerDispatch(_encoding, exclude=[pickle])

save = IO_HANDLER.save  # pylint: disable=invalid-name
load = IO_HANDLER.load  # pylint: disable=invalid-name
