# header.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file editor widget event handlers."""

import tkinter

from ..core import constants
from ..core import sequences
from ..core import header_inserter
from ..core import content
from ..core import deleter
from . import menus
from . import method_makers


class HeaderError(Exception):
    """Exception class for header module."""


class Header(menus.Menus):
    """Delegate to superclass then bind events to methods.

    The events on the Text widget for the editor are bound to methods
    of Header.

    The Header class supports the 'EVENT DETAILS' part of an ECF results
    submission file by default.

    """

    _TITLE_SUFFIX = "   <Event Details>"
    _sequences = (sequences.HEADER_SEQUENCES,)
    _allowed_inserts = {
        (
            constants.EVENT_DETAILS,
            constants.EVENT_DETAILS,
        ): constants.EVENT_DETAILS_FIELD_TAGS
    }
    _popup_menu_label_map = {
        constants.COMMENT_LIST.capitalize(): constants.COMMENT.capitalize(),
        constants.COMMENT_PIN.capitalize(): constants.COMMENT.capitalize(),
    }
    _NEW_FILE_TEXT = "\n".join(
        (
            "#EVENT DETAILS",
            "#EVENT CODE=",
            "#EVENT NAME=",
            "#SUBMISSION INDEX=",
            "#EVENT DATE=",
            "#FINAL RESULT DATE=",
            "#RESULTS OFFICER=",
            "#RESULTS OFFICER ADDRESS=",
            "#TREASURER=",
            "#TREASURER ADDRESS=",
            "#MOVES FIRST SESSION=",
            "#MINUTES FIRST SESSION=",
            "#MOVES SECOND SESSION=",
            "#MINUTES SECOND SESSION=",
            "#ADJUDICATED=",
            "#FINISH",
        )
    )

    def __init__(self, **kargs):
        """Delegate **kargs to superclass then bind Text widget events.

        The initial state is 'file not open' but the 'Alt-KeyPress'
        sequences to invoke menubar options are always available.

        """
        super().__init__(**kargs)
        widget = self.widget
        self.bind(widget, "<Alt-KeyPress-f>", function=self.return_continue)
        self.bind(widget, "<Alt-KeyPress-s>", function=self.return_continue)
        self.bind(widget, "<Alt-KeyPress-h>", function=self.return_continue)

        # Prevent the implied adjustment of CURRENT mark from affecting the
        # selection of context in _get_bindings_context_after_buttonpress()
        # method.
        # A side effect is suppressing the useless highlighting of what would
        # be the selection of word or line.
        # Perception might be pointer clicks repeated quickly are ignored,
        # rather than double or triple clicks are doing nothing.
        self.bind(widget, "<Double-ButtonPress-1>", function=self.return_break)
        self.bind(widget, "<Triple-ButtonPress-1>", function=self.return_break)

        # Prevent useless highlighting of what would be the selection by
        # gentle drag of pointer while button-1 pressed.
        # Sufficiently abrupt motion does this highlighting even with Double,
        # Triple, and Quadruple, modifiers: so I assume my understanding of
        # motion events is not good enough.
        # Observed with X-server and client on different boxes both OpenBSD.
        self.bind(widget, "<Motion>", function=self.return_break)

        # Allow F10 to initiate a menu selection.
        self.bind(widget, "<F10>", function=self.return_none)
        self.bind(widget, "<Alt-F10>", function=self._show_popup_menu_alt_f10)

        self._define_scrolling_methods()
        self._scroll_menu = tkinter.Menu(master=self.popup_menu, tearoff=False)
        self._add_scrolling_commands_to_popup_menu()

        self._bind_events_file_not_open()
        self.set_frozen_bindings()
        self.popup_menu.bind("<Unmap>", self.try_event(self.return_none))
        self.popup_menu.bind("<Map>", self.try_event(self.return_none))

    def close_file(self):
        """Delegate then destroy bindings."""
        super().close_file()
        if not self.filename:
            self.unbind_all_handlers_except_frozen()
            self._bind_events_file_not_open()

    def file_open(self):
        """Delegate then apply bindings."""
        super().file_open()
        if self.filename:
            self.unbind_all_handlers_except_frozen()
            self._bind_events_file_open()

    def file_new(self):
        """Delegate then apply bindings."""
        super().file_new()
        if self.filename:
            self.unbind_all_handlers_except_frozen()
            self._bind_events_file_open()

    def _handle_up_one_line(self):
        """Handle previous line event."""
        self.widget.yview_scroll(-1, "units")

    def _handle_down_one_line(self):
        """Handle next line event."""
        self.widget.yview_scroll(1, "units")

    def _handle_up_one_page(self):
        """Handle previous page event."""
        self.widget.yview_scroll(-1, "pages")

    def _handle_down_one_page(self):
        """Handle next page event."""
        self.widget.yview_scroll(1, "pages")

    def _handle_see_insert(self):
        """Handle show insert cursor event."""
        self.widget.see(tkinter.INSERT)

    def _handle_move_insert_to_middle_line_start(self):
        """Handle move insert cursor menu action."""
        widget = self.widget
        widget.mark_set(
            tkinter.INSERT,
            widget.index("@0," + str(widget.winfo_height() // 2)),
        )

    def _handle_next_field(self):
        """Handle move to next field event."""
        # Without the "+1c" in the mark_next() call at top of while loop
        # Down key events do not move the 'insert' mark from it's current
        # location if already at a 'FIELD_VALUE_TAG' mark.
        # Navigation around the text displayed by 'File | New' misses out
        # one location if the pointer is clicked to the right of the text.
        # One location is also missed out if the pointer is clicked in the
        # text and the pointer is moved to the right of the text.  Move
        # the pointer back into the text, with or without clicking, to get
        # all locations visted again.
        # No locations are missed if the clicked line has text to the right
        # of the '=' character when initially displayed: unless pointer is
        # clicked exactly between the '=' and adjacent character on right.
        # (Editing not supported yet.)
        widget = self.widget
        next_ = tkinter.INSERT
        while True:
            next_ = widget.mark_next(next_ + "+1c")
            if not next_:
                next_ = self.content.get_next_mark_after_start(widget, "1.0")
                if next_:
                    widget.mark_set(tkinter.INSERT, next_)
                break
            if next_.startswith(constants.FIELD_VALUE_TAG):
                widget.mark_set(tkinter.INSERT, next_)
                break
        context = self._get_bindings_context_after_up_or_down()
        self._set_bindings_context_and_ensure_visible(context)

    def _handle_prior_field(self):
        """Handle move to previous field event."""
        widget = self.widget
        prior = tkinter.INSERT
        while True:
            prior = widget.mark_previous(prior)
            if not prior:
                prior = tkinter.END
                while True:
                    prior = widget.mark_previous(prior)
                    if not prior:
                        break
                    if prior.startswith(constants.FIELD_VALUE_TAG):
                        widget.mark_set(tkinter.INSERT, prior)
                        break
                break
            if prior.startswith(constants.FIELD_VALUE_TAG):
                if widget.compare(prior, "!=", tkinter.INSERT):
                    widget.mark_set(tkinter.INSERT, prior)
                    break
        context = self._get_bindings_context_after_up_or_down()
        self._set_bindings_context_and_ensure_visible(context)

    def _set_bindings_context_and_ensure_visible(self, context):
        """Set bindings for context and ensure context field is visible."""
        self._set_bindings_for_context(context)
        self._set_colours_and_see()

    def _handle_left_one_char_in_field(self):
        """Handle left one character in value event."""
        widget = self.widget
        range_ = self._value_range_containing_insert_mark()
        if (
            range_
            and widget.compare(range_[0], "<", tkinter.INSERT)
            and widget.compare(range_[1], ">=", tkinter.INSERT)
        ):
            widget.mark_set(tkinter.INSERT, tkinter.INSERT + "-1c")

    def _handle_right_one_char_in_field(self):
        """Handle right one character in value event."""
        widget = self.widget
        range_ = self._value_range_containing_insert_mark()
        if range_:
            if widget.compare(
                range_[0], "<=", tkinter.INSERT
            ) and widget.compare(range_[1], ">", tkinter.INSERT):
                widget.mark_set(tkinter.INSERT, tkinter.INSERT + "+1c")
        else:
            range_ = widget.tag_nextrange(
                constants.FIELD_VALUE_TAG, tkinter.INSERT
            )
            if range_ and widget.compare(range_[0], "==", tkinter.INSERT):
                widget.mark_set(tkinter.INSERT, tkinter.INSERT + "+1c")

    def _handle_delete_left_one_char_in_field(self):
        """Handle delete one character on left of INSERT event."""
        widget = self.widget
        range_ = self._value_range_containing_insert_mark()
        if (
            range_
            and widget.compare(range_[0], "<", tkinter.INSERT)
            and widget.compare(range_[1], ">=", tkinter.INSERT)
        ):
            widget.mark_set(tkinter.INSERT, tkinter.INSERT + "-1c")
            widget.delete(tkinter.INSERT)
            self._delete_empty_value()

    def _handle_delete_right_one_char_in_field(self):
        """Handle delete one character on right of INSERT event."""
        widget = self.widget
        range_ = self._value_range_containing_insert_mark()
        if range_:
            if widget.compare(
                range_[0], "<=", tkinter.INSERT
            ) and widget.compare(range_[1], ">", tkinter.INSERT):
                widget.delete(tkinter.INSERT)
                self._delete_empty_value()
        else:
            range_ = widget.tag_nextrange(
                constants.FIELD_VALUE_TAG, tkinter.INSERT
            )
            if range_ and widget.compare(range_[0], "==", tkinter.INSERT):
                widget.delete(tkinter.INSERT)
                self._delete_empty_value()

    def _handle_start_of_field(self):
        """Handle move INSERT to start of value event."""
        widget = self.widget
        range_ = self._value_range_containing_insert_mark()
        if range_:
            widget.mark_set(tkinter.INSERT, range_[0])

    def _handle_end_of_field(self):
        """Handle move INSERT to end of value event."""
        widget = self.widget
        range_ = self._value_range_containing_insert_mark()
        if range_:
            widget.mark_set(tkinter.INSERT, range_[1])

    def _handle_first_field(self):
        """Handle move INSERT to first field event."""
        widget = self.widget
        ranges = widget.tag_ranges(constants.FIELD_VALUE_TAG)
        if ranges:
            widget.mark_set(tkinter.INSERT, widget.index(ranges[0]))
            self._set_colours_and_see()

    def _handle_last_field(self):
        """Handle move INSERT to last field event."""
        widget = self.widget
        ranges = widget.tag_ranges(constants.FIELD_VALUE_TAG)
        if ranges:
            widget.mark_set(tkinter.INSERT, widget.index(ranges[-2]))
            self._set_colours_and_see()

    def _delete_empty_value(self):
        """Delete the elided space characters surrounding the value."""
        if not self.content.value_edge:
            return
        widget = self.widget
        range_ = widget.tag_prevrange(
            constants.UI_VALUE_BOUNDARY_TAG, tkinter.INSERT
        )
        if (
            range_
            and widget.compare(range_[0], "==", tkinter.INSERT + "-1c")
            and widget.compare(range_[1], "==", tkinter.INSERT + "+1c")
        ):
            widget.delete(*range_)

    @staticmethod
    def _dismiss(event=None):
        """Do nothing for keypress equivalent Escape of dismiss popup menu."""
        del event
        print("dismiss")
        return "break"

    def _create_inserter(self):
        """Create the application's inserter instance.

        The inserter is an instance of header_inserter.HeaderInserter class.

        Subclasses should override this method to create an instance of a
        suitable subclass of HeaderInserter.

        """
        self._inserter = header_inserter.HeaderInserter()

    def _show_popup_menu_alt_f10(self, event):
        """Handle <Alt-F10> event.

        Adjust bindings to fit location of INSERT mark.

        Reset the highlight colours if clicked on a character tagged with
        'value'.

        Show popup menu at CURRENT mark location relevant to tag combination
        at INSERT mark location.

        """
        assert event.widget is self.widget

        # Alt-F10 is a frozen binding so check popup menu is relevant,
        # and treat as F10 if not.
        if not self.filename:
            return None

        context = self._get_bindings_context_at_insert_mark()
        if self._set_bindings_for_context(context):
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def _bind_events_file_open(self):
        """Bind events to methods for actions on an open file.

        The 'Alt' bindings to access menubar options are not changed.

        The Bindings.unbind_all_handlers_except_frozen() method should be
        called first to remove any context dependent bindings.

        """
        self._bind_active_editor_actions()

    def _bind_events_file_not_open(self):
        """Bind events to methods for file not open.

        The 'Alt' bindings to access menubar options are not changed.

        The Bindings.unbind_all_handlers_except_frozen() method should be
        called first to remove any context dependent bindings.

        """
        widget = self.widget
        self.bind(widget, "<KeyPress>", function=self._start_hint)
        self.bind(widget, "<ButtonPress-1>", function=self._start_hint)

    def _keypress_alt_delete(self, event):
        """Event handler for 'Alt-KeyPress-Delete' sequence."""
        del event
        self._command_alt_delete()
        return "break"

    def _command_alt_insert(self):
        """Commant handler for 'Alt-Insert' menu option."""
        widget = self.widget
        if widget.get("1.0") == "#":
            delimiter = "\n"
        else:
            delimiter = "\n#"
        text = delimiter.join(
            (
                "#" + constants.NAME_EVENT_DETAILS,
                widget.get("1.0", tkinter.END),
            )
        )
        conf = self._make_configuration()
        parser = content.Content(
            text,
            self._show_value_boundary(conf),
            None,
        )
        self.content = parser.parse(self.widget, stop_at=None)

    def _keypress_alt_insert(self, event):
        """Event handler for 'Alt-KeyPress-Insert' sequence."""
        del event
        self._command_alt_insert()
        return "break"

    def _command_alt_delete(self):
        """Commant handler for 'Alt-Delete' menu option.

        The INSERT mark ends up on a '#' character when a field is deleted
        where the context is None.  No inserts or deletes will be possible
        until the INSERT mark is moved: thus bindings are not recalculated.

        """
        if self._inserter.context is None:
            return
        deleter.delete_fields(self.widget)

    # Introduced to avoid pylint 'protected-access' warning in menus module
    # _define_insert_method() function.
    # Method defined in Header because _inserter attribute is defined here.
    def insert_fields(self, key):
        """Delegate to self._inserter.insert_fields method.

        Recalculate bindings to remove insert field binding from allowed
        bindings.

        """
        self._inserter.insert_fields(key, self.widget, self.content)
        context = self._get_bindings_context_at_insert_mark()
        self._set_bindings_for_context(context)

    # Diagnostic tool.
    def _show_bindings(self, context):
        """Show bindings chosen for insert context."""
        if context == self._inserter.context:
            print("\n", "not changed", context)
            return
        if context is None:
            print("\n", context)
            return
        part, record, field, part_id, record_id, siblings = context
        del siblings
        print("\n", part, record, field, part_id, record_id)
        method_name_suffix = sequences.method_name_suffix
        for items in self._sequences:
            for seq, spart, srecord, sfields, basename in items[:-1]:
                if spart == part and srecord == record and field in sfields:
                    print(seq, "\t", "\t", "\t", method_name_suffix(basename))


method_makers.define_sequence_insert_map_insert_methods(
    class_=Header,
    map_=header_inserter.sequence_insert_map,
    sequence=sequences.HEADER_SEQUENCES,
)
