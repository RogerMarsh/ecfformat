# help_.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to create Help widgets for ECF Format Editor."""

import tkinter

from solentware_misc.gui.help_ import help_widget

from .. import help_


def help_about(master):
    """Display About document."""
    help_widget(master, help_.ABOUT, help_)


def help_guide(master):
    """Display Guide document."""
    help_widget(master, help_.GUIDE, help_)


def help_keyboard(master):
    """Display Keyboard actions document."""
    help_widget(master, help_.ACTIONS, help_)


if __name__ == "__main__":
    # Display all help documents without running ChessResults application

    root = tkinter.Tk()
    help_about(root)
    help_guide(root)
    help_keyboard(root)
    root.mainloop()
