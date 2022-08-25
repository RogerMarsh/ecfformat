# method_makers.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to create event handler methods for Editor and subclasses.

The methods created are those which insert fields into an Editor instance
taking into account what fields are present and absent.

Sequences of '#<name>=' are the things inserted by the insert_fields method
called by the generated methods, where the user is expected to supply a
value after the '='.

"""
from ..core import sequences


def _define_insert_method(sequence_insert_map_item):
    """Define method to insert sequence_insert_map_item fields into widget.

    The defined method is expected to be called in response to an event in
    tkinter where no further event handlers should be called.

    """
    # self is not an instance of Header, or a subclass, here so attracts a
    # 'protected-access' warning from pylint if the 'self._inserter' method
    # is called directly.
    # Probably it should not be called directly because the 'return "break"'
    # statement makes tkinter do what is needed after the callback action.
    def method(self):
        self.insert_fields(sequence_insert_map_item[4][0])
        return "break"

    method.__doc__ = sequence_insert_map_item[0].join(("Handle ", " event."))
    return method


def define_sequence_insert_map_insert_methods(
    class_=None, map_=None, sequence=None
):
    """Define insert_* methods in class_ for items in sequence.

    This method is provided to define insert_* methods, not yet in class_,
    in modules which implement subclasses of Inserter.

    class_ is the class where the methods are to be defined.
    map_ should be the sequence_insert_map attribute whose keys imply the
    method name insert_<key>.
    sequence should be the appropriate *_SEQUENCES attribute in sequences
    module.

    """
    if class_ is None or map_ is None or sequence is None:
        return
    for item in sequence:
        method_name = "_".join(
            ("_handle", sequences.method_name_suffix(item[4]))
        )
        if item[4][0] not in map_:
            continue
        if hasattr(class_, method_name):
            continue
        setattr(class_, method_name, _define_insert_method(item))
