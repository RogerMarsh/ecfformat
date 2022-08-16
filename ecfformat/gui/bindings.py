# bindings.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide interface to tkinter bind and unbind methods.

Tcl/Tk uses the bind command to bind and unbind sequences; where giving the
empty string implements the removal of the current binding.

Adopting the same technique with the tkinter bind method causes a memory
leak.  The Python idiom is 'id = w.bind(seq); w.unbind(seq, funcid=a)',
where unbind calls Tcl/Tk bind the Tcl/Tk way, and avoids memory leaks.

This technique is described in the docstrings for tkinter bind and unbind.

(I managed to not notice this point for 20 years!; using tkinter bind as if
it were Tcl/Tk bind.)

"""

from solentware_misc.gui.exceptionhandler import ExceptionHandler


class Bindings(ExceptionHandler):
    """Keep register of tkinter bind returns for use by tkinter unbind.

    _bindings is the register with (widget, sequence) as the key and the
    function identifier returned by tkinter's bind() method as the value.

    _current_binding can be used to control changes to _bindings and whether
    there should be a need to adjust bindings.  The protocol is chosen to
    fit the application.  Initial value is None, intended to mean 'clear
    the register before applying new bindings'.

    """

    def __init__(self):
        """Initialize the bindings register."""
        self._bindings = {}
        self._current_binding = None
        self._frozen_bindings = set()

    def bind(self, widget, sequence, function=None, add=None):
        """Bind sequence to function for widget and note binding identity.

        If a binding exists for widget for sequence it is destroyed.

        If function is not None a new binding is created and noted.

        """
        key = (widget, sequence)
        if key in self._bindings and add is None:
            widget.unbind(sequence, funcid=self._bindings[key])
            del self._bindings[key]
        if function is not None:
            self._bindings[key] = widget.bind(
                sequence=sequence, func=self.try_event(function), add=add
            )

    def unbind_all_except_frozen(self):
        """Unbind registered sequences which are not in _frozen_bindings."""
        for key in set(self._bindings).difference(self._frozen_bindings):
            key[0].unbind(key[1], funcid=self._bindings[key])
            del self._bindings[key]
        self._current_binding = None

    def unbind_all(self):
        """Unbind all registered sequences."""
        for key, funcid in self._bindings.items():
            key[0].unbind(key[1], funcid=funcid)
        self._bindings.clear()
        self._current_binding = None

    def set_frozen_bindings(self):
        """Set _frozen_bindings to set of _bindings' keys."""
        self._frozen_bindings.clear()
        self._frozen_bindings.update(self._bindings)

    def unset_frozen_bindings(self):
        """Set _frozen_bindings to empty."""
        self._frozen_bindings.clear()

    @staticmethod
    def return_break(event):
        """Do nothing and return 'break' in response to event."""
        del event
        return "break"

    @staticmethod
    def return_continue(event):
        """Do nothing and return 'continue' in response to event."""
        del event
        return "continue"

    @staticmethod
    def return_none(event):
        """Do nothing and return None in response to event."""
        del event
