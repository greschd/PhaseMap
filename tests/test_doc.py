# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import sys

import fsc.export


# This should never appear in any serious code ;)
# To out-manoeuver pickle's caching, and force re-loading phasemap
def test_all_doc():
    old_name = "phasemap"
    new_name = "hoopy_phasemap"
    for key in list(sys.modules.keys()):
        # move previous phasemap to hoopy_phasemap
        if key.startswith(old_name):
            new_key = key.replace(old_name, new_name)
            sys.modules[new_key] = sys.modules[key]
            del sys.modules[key]
    fsc.export.test_doc()
    try:
        import phasemap  # pylint: disable=import-outside-toplevel,unused-import
    finally:
        # reset to the previous phasemap -- just doing import breaks pickle
        for key in list(sys.modules.keys()):
            if key.startswith(old_name):
                del sys.modules[key]
        for key in list(sys.modules.keys()):
            if key.startswith(new_name):
                new_key = key.replace(new_name, old_name)
                sys.modules[new_key] = sys.modules[key]
                del sys.modules[key]
