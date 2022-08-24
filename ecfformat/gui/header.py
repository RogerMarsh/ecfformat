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
from . import editor

# Define scrolling events and commands.
_ACTIONS = (
    ("<KeyPress-Down>", "next_field", "Next value", "Down"),
    ("<KeyPress-Up>", "prior_field", "Previous value", "Up"),
    ("<KeyPress-Left>", "left_one_char_in_field", "Left 1 char", "Left"),
    ("<KeyPress-Right>", "right_one_char_in_field", "Right 1 char", "Right"),
    (
        "<KeyPress-BackSpace>",
        "delete_left_one_char_in_field",
        "Delete left",
        "Backspace",
    ),
    (
        "<KeyPress-Delete>",
        "delete_right_one_char_in_field",
        "Delete right",
        "Delete",
    ),
    ("<KeyPress-Home>", "start_of_field", "Value start", "Home"),
    ("<KeyPress-End>", "end_of_field", "Value end", "End"),
    ("<Alt-KeyPress-Up>", "first_field", "First field", "Alt-Up"),
    ("<Alt-KeyPress-Down>", "last_field", "Last field", "Alt-Down"),
    ("<KeyPress-Prior>", "up_one_line", "Previous line", "PgUp (Prior)"),
    ("<KeyPress-Next>", "down_one_line", "Next line", "PgDn (Next)"),
    ("<Shift-KeyPress-Prior>", "up_one_page", "Previous page", "Shift-PgUp"),
    ("<Shift-KeyPress-Next>", "down_one_page", "Next page", "Shift-PgDn"),
    (
        "<Control-KeyPress-Prior>",
        "see_insert",
        "Go to insert point",
        "Control-PgUp",
    ),
    (
        "<Control-KeyPress-Next>",
        "move_insert_to_middle_line_start",
        "Move insert point",
        "Control-PgDn",
    ),
)


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
        self._create_inserter()
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
            self.unbind_all_except_frozen()
            self._bind_events_file_not_open()

    def file_open(self):
        """Delegate then apply bindings."""
        super().file_open()
        if self.filename:
            self.unbind_all_except_frozen()
            self._bind_events_file_open()

    def file_new(self):
        """Delegate then apply bindings."""
        super().file_new()
        if self.filename:
            self.unbind_all_except_frozen()
            self._bind_events_file_open()

    def _define_scrolling_methods(self):
        """Define methods for scrolling."""
        self._define_scrolling_event_and_command_handlers(_ACTIONS)

    def _add_scrolling_commands_to_popup_menu(self):
        """Set commands for scrolling."""
        for item in _ACTIONS:
            command = getattr(self, "_command_" + item[1])
            self._scroll_menu.add_command(
                label=item[2], command=command, accelerator=item[3]
            )

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

    def _set_bindings_for_context(self, context):
        """Return False if EVENT DETAILS starts text and context is None.

        The return value is for calls when displaying a popup menu and is
        ignored otherwise.

        """
        if context is None:
            self._unset_current_context_bindings()
            widget = self.widget
            first_field = widget.tag_nextrange(constants.FIELD_NAME_TAG, "1.0")
            if (
                first_field
                and widget.compare(first_field[0], "==", "1.1")
                and constants.EVENT_DETAILS in widget.tag_names(first_field[0])
            ):
                return False
            self._set_insert_event_details_binding()
        else:
            self._set_bindings(context)
            self._set_field_delete_binding()
        self._show_scroll_bindings_on_popup_menu()
        return True

    def _set_bindings_context_and_ensure_visible(self, context):
        """Set bindings for context and ensure context field is visible."""
        self._set_bindings_for_context(context)
        self._set_colours_and_see()

    def _set_colours_and_see(self, index=tkinter.INSERT):
        """Set highlight colours of field at index and ensure it is seen.

        index is usually tkinter.INSERT but it can be necessary to set at
        some other value.

        """
        widget = self.widget
        for highlight_tag in (
            constants.UI_NAME_HIGHLIGHT_TAG,
            constants.UI_VALUE_HIGHLIGHT_TAG,
        ):
            ranges = widget.tag_ranges(highlight_tag)
            if ranges:

                # Before adding an event handler for <ButtonPress-1> to fix
                # <KeyPress-Tab>, for example, after editing several values
                # selected by <ButtonPress-1> leaving multiple ranges for the
                # two highlighting tags, which breaks the tkinter tag_remove
                # interface, the following hack straight to the underlying
                # tk code (assumed) was seen to work.
                # Hack restored after problem seen after typing in an area
                # with the value tag, moving to another by pointer, and type
                # something in the new area.
                # Here replacing '*ranges' by 'ranges[0], ranges[-1]' is fine.
                # widget.tag_remove(highlight_tag, *ranges)
                # widget.tk.call(
                #     widget._w,
                #     "tag",
                #     "remove",
                #     highlight_tag,
                #     *ranges,
                # )
                widget.tag_remove(highlight_tag, ranges[0], ranges[-1])

        range_ = widget.tag_prevrange(constants.FIELD_NAME_TAG, index + "+1c")
        if range_:
            widget.tag_add(constants.UI_NAME_HIGHLIGHT_TAG, *range_)
            range_ = widget.tag_nextrange(
                constants.FIELD_VALUE_TAG,
                range_[1],
                index + "+1c",
            )
            if range_:
                widget.tag_add(
                    constants.UI_VALUE_HIGHLIGHT_TAG,
                    range_[0],
                    range_[1],
                )
        widget.see(index)

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

    def _insert_char_in_value(self, event=None):
        """Handle <KeyPress> event.

        A character can be inserted in a region tagged as a value.  Marks
        indicate where these regions can be started.

        """
        char = event.char
        if char == "" or not char.isprintable():
            return "break"
        widget = event.widget
        assert widget is self.widget

        # Insert character into empty value.
        if widget.get(
            tkinter.INSERT + "-1c"
        ) == constants.NAME_VALUE_SEPARATOR and not widget.tag_names(
            tkinter.INSERT
        ):
            self.content.insert_tagged_char_at_mark(self.widget, char)
            self._set_colours_and_see()
            return "break"

        range_ = self._value_range_containing_insert_mark()
        if range_:

            # For years the tkinter.__init__.Text.insert() docstring has
            # persuaded me to avoid passing any arguments in *args, but
            # do tagging in particular by a tag_add() call immediately
            # after.  In particular the reference to 'An additional tag ...'.
            # Perhaps because I was checking 'widget.tag_names(range_[0])'
            # is picking the correct tags, tried the call here and found
            # it works as I would expect from the Tcl/Tk manual page!!!
            widget.insert(
                widget.index(tkinter.INSERT),
                char,
                widget.tag_names(range_[0])
                + (constants.UI_VALUE_HIGHLIGHT_TAG,),
            )

        return "break"

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

    def _set_bindings_and_highlight(self, event=None):
        """Handle <ButtonPress-1> event.

        Adjust bindings to fit location of INSERT mark.

        Reset the highlight colours if clicked on a character tagged with
        'value'.

        """
        widget = event.widget
        assert widget is self.widget
        context = self._get_bindings_context_after_buttonpress()
        self._set_bindings_for_context(context)
        range_ = self._value_range_nearest_current_mark()
        if (
            range_
            and widget.compare(range_[0], "<=", tkinter.CURRENT)
            and widget.compare(range_[1], ">=", tkinter.CURRENT)
        ):
            self._set_colours_and_see(range_[0])
        elif self._inserter.context is None:
            self._set_bindings((None, None, None, None, None, frozenset()))

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

    def _show_popup_menu(self, event):
        """Handle <ButtonPress-3> event.

        Move INSERT mark to CURRENT mark (where event happened).

        Adjust bindings to fit location of INSERT mark.

        Reset the highlight colours if clicked on a character tagged with
        'value'.

        Show popup menu relevant to tag combination at pointer location.

        """
        assert event.widget is self.widget

        # _get_bindings_context_after_buttonpress() does not currently depend
        # on tkinter.INSERT but perhaps could; while the new value for
        # tkinter.INSERT is set before _unset_current_context_bindings() and
        # _set_bindings() calls elsewhere.
        # Some bindings for badly formatted files depend on the new setting
        # of tkinter.INSERT in particular insert EVENT DETAILS.
        context = self._get_bindings_context_after_buttonpress()
        self.widget.mark_set(tkinter.INSERT, tkinter.CURRENT)

        if self._set_bindings_for_context(context):
            self.popup_menu.tk_popup(event.x_root, event.y_root)

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

    def _inhibit_binding(self, inhibit):
        """Return True if self.widget has text tagged with a tag in inhibit."""
        for tag in inhibit:
            if self.widget.tag_ranges(tag):
                return True
        return False

    def _set_bindings(self, context):
        """Set KeyPress and popup menu bindings for field at context.

        Assume bindings are set correctly if the context has not changed.

        """
        self._unset_current_context_bindings()
        if context is None:
            return
        self._inserter.context = context
        part = self._inserter.context.part
        record = self._inserter.context.record
        field = self._inserter.context.field
        siblings = self._inserter.context.siblings
        method_name_suffix = sequences.method_name_suffix
        for items in self._sequences:
            for seq, spart, srecord, sfields, sname, inhibit in items:
                if siblings.intersection(sname[-1]):
                    continue
                if self._inhibit_binding(inhibit):
                    continue
                if spart == part and srecord == record and field in sfields:
                    self._set_event_and_command_bindings(
                        seq, method_name_suffix(sname), sname[0]
                    )

    def _set_field_delete_binding(self):
        """Bind Alt-KeyPress-Delete for location of tkinter.INSERT mark.

        A field or set of fields may be deleted when the insert mark is in a
        field name.  The self._delete method will choose the appropriate if
        invoked.

        """
        widget = self.widget
        tag_names = set(widget.tag_names(widget.index(tkinter.INSERT)))
        if constants.FIELD_VALUE_TAG in tag_names:
            return
        if constants.FIELD_NAME_TAG in tag_names:
            self.popup_menu.add_separator()
            self._set_event_and_command_bindings(
                "<Alt-Delete>", "alt_delete", "Delete Field"
            )

    def _show_scroll_bindings_on_popup_menu(self):
        """Advertize scrolling bindings."""
        self.popup_menu.add_separator()
        self.popup_menu.add_cascade(
            label="Scrolling Actions", menu=self._scroll_menu
        )

    def _set_insert_event_details_binding(self):
        """Bind Alt-KeyPress-Insert for location of tkinter.INSERT mark.

        An EVENT DETAILS field may be inserted immediately before the first
        "#" if the insert point is not tagged constants.FIELD_VALUE_TAG.

        """
        widget = self.widget
        tag_names = set(widget.tag_names(widget.index(tkinter.INSERT)))
        if constants.FIELD_VALUE_TAG not in tag_names:
            self._set_event_and_command_bindings(
                "<Alt-Insert>", "alt_insert", "Insert Event Details"
            )

    def _set_event_and_command_bindings(self, sequence, suffix, label):
        """Set bindings for sequence as methods named *_<suffix>."""
        self.bind(
            self.widget,
            sequence,
            function=getattr(self, "_keypress_" + suffix),
        )
        self.popup_menu.add_command(
            label=self._popup_menu_label_map.get(label, label),
            command=getattr(self, "_command_" + suffix),
            accelerator=sequence.lstrip("<").rstrip(">"),
        )

    def _unset_current_context_bindings(self):
        """Clear KeyPress and popup menu bindings for context being discarded.

        The context is held in self._inserter attribute.

        """
        widget = self.widget
        self.bind(widget, "<Alt-KeyPress-Delete>")
        self.popup_menu.delete(0, tkinter.END)
        if self._inserter.context is None:
            return
        part = self._inserter.context.part
        record = self._inserter.context.record
        field = self._inserter.context.field
        for items in self._sequences:
            for seq, spart, srecord, sfields, basename, inhibit in items:
                del basename
                del inhibit
                if spart == part and srecord == record and field in sfields:
                    self.bind(widget, seq)
        self._inserter.context = None

    def _bind_events_file_open(self):
        """Bind events to methods for actions on an open file.

        The 'Alt' bindings to access menubar options are not changed.

        The Bindings.unbind_all_except_frozen() method should be called first
        to remove any context dependent bindings.

        """
        widget = self.widget
        self.bind(widget, "<KeyPress>", function=self._insert_char_in_value)
        self.bind(
            widget,
            "<ButtonPress-1>",
            function=self._set_bindings_and_highlight,
        )
        self.bind(widget, "<ButtonPress-3>", function=self._show_popup_menu)
        for item in _ACTIONS:
            function = getattr(self, "_keypress_" + item[1])
            self.bind(widget, item[0], function=function)

        widget.mark_set(tkinter.INSERT, "1.0")
        self._set_bindings((None, None, None, None, None, frozenset()))

    def _bind_events_file_not_open(self):
        """Bind events to methods for file not open.

        The 'Alt' bindings to access menubar options are not changed.

        The Bindings.unbind_all_except_frozen() method should be called first
        to remove any context dependent bindings.

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


editor.define_sequence_insert_map_insert_methods(
    class_=Header,
    map_=header_inserter.sequence_insert_map,
    sequence=sequences.HEADER_SEQUENCES,
)
