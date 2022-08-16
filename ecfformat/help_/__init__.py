# __init__.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Help files for ECF results submission file editor."""

import os

ABOUT = "About"
GUIDE = "Guide"
ACTIONS = "Actions"

_textfile = {
    ABOUT: ("aboutformatter",),
    GUIDE: ("guide",),
    ACTIONS: ("keyboard",),
}

folder = os.path.dirname(__file__)

for k in list(_textfile.keys()):
    _textfile[k] = tuple(
        os.path.join(folder, ".".join((n, "txt"))) for n in _textfile[k]
    )

del folder, k, os
