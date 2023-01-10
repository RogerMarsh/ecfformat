# editor.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file editor framework and menus."""

import tkinter
import tkinter.messagebox
import tkinter.filedialog

from solentware_misc.workarounds.workarounds import (
    text_get_displaychars,
    text_delete_ranges,
)
from solentware_bind.gui import bindings

from . import help_
from .. import APPLICATION_NAME
from ..core import constants
from ..core import configuration
from ..core import fields
from ..core import sequences
from ..core import inserter

STARTUP_MINIMUM_WIDTH = 800
STARTUP_MINIMUM_HEIGHT = 400

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


class Editor(bindings.Bindings):
    """Define menus and text widget for ECF results submission file editor."""

    encoding = "utf-8"
    _TITLE_SUFFIX = ""
    _sequences = ()
    _allowed_inserts = {}
    _popup_menu_label_map = {}
    _NO_VALUE_TAGS = None

    def __init__(
        self,
        root=None,
        application_name=APPLICATION_NAME,
        width=None,
        height=None,
        **kargs,
    ):
        """Create the file and GUI objects.

        **kargs - passed to tkinter Toplevel widget if use_toplevel True

        """
        super().__init__()
        self.application_name = application_name
        if root is None:
            root = tkinter.Toplevel(**kargs)
        if width is None:
            width = STARTUP_MINIMUM_WIDTH
        if height is None:
            height = STARTUP_MINIMUM_HEIGHT
        self.root = root
        root.wm_title(self.set_title_suffix(None))
        root.wm_minsize(width=width, height=height)
        self._create_inserter()
        self._create_menubar_menus()
        widget = tkinter.Text(
            master=root, wrap="word"
        )  # , undo=tkinter.FALSE)
        scrollbar = tkinter.Scrollbar(
            master=root, orient=tkinter.VERTICAL, command=widget.yview
        )
        widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        widget.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        widget.tag_configure(
            constants.TAG_ERROR_UNKNOWN, background="aquamarine"
        )
        widget.tag_configure(
            constants.TAG_ERROR_UNEXPECTED, background="azure"
        )
        widget.tag_configure(
            constants.TAG_ERROR_TABLE_LAYOUT, background="honeydew2"
        )
        widget.tag_configure(
            constants.UI_NAME_HIGHLIGHT_TAG, background="AntiqueWhite1"
        )
        widget.tag_configure(
            constants.UI_VALUE_HIGHLIGHT_TAG, background="AntiqueWhite"
        )
        widget.focus_set()
        self.widget = widget
        self.popup_menu = tkinter.Menu(master=self.widget, tearoff=False)
        self._scroll_menu = tkinter.Menu(master=self.popup_menu, tearoff=False)
        self.content = None
        self._define_event_and_command_handlers()

    def _create_menubar_menus(self):
        """Create the menus for application.

        Subclasses should override this method to create their menubar.

        """

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

    def _bind_active_editor_actions(self):
        """Bind events defined in editor._ACTIONS tuple."""
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

    def _define_event_and_command_handlers(self):
        """Define event and command handlers for application.

        The class attribute _sequences has elements from which the keypress
        event and popup menu command handler method names are derived.

        The two *_<derived name> methods are alternative ways of invoking
        the _handle_<derived name> method.

        """
        method_name_suffix = sequences.method_name_suffix
        for items in self._sequences:
            for item in items:
                suffix = method_name_suffix(item[4])
                handler = "_handle_" + suffix
                assert hasattr(self, handler)
                self._define_event_handler(suffix, handler)
                self._define_command_handler(suffix, handler)

    def _define_event_handler(self, suffix, handler):
        """Define _keypress_<suffix> method if it does not exist."""
        method_name = "_keypress_" + suffix
        if hasattr(self, method_name):
            return

        def method():
            def keypress(event):
                assert event.widget is self.widget
                getattr(self, handler)()
                return "break"

            return keypress

        setattr(self, method_name, method())
        return

    def _define_command_handler(self, suffix, handler):
        """Define _command_<suffix> method if it does not exist."""
        method_name = "_command_" + suffix
        if hasattr(self, method_name):
            return

        def method():
            def command():
                getattr(self, handler)()
                return "break"

            return command

        setattr(self, method_name, method())
        return

    def set_title_suffix(self, title):
        """Return application title. Default is application name."""
        if title is None:
            return self.application_name
        return "".join((title, self._TITLE_SUFFIX))

    def help_about(self):
        """Display information about EmailExtract."""
        help_.help_about(self.root)

    def help_guide(self):
        """Display brief User Guide for EmailExtract."""
        help_.help_guide(self.root)

    def help_keyboard(self):
        """Display technical notes about EmailExtract."""
        help_.help_keyboard(self.root)

    def _hide_value_boundaries(self):
        """Adjust settings to hide value boundaries."""
        self._make_configuration().set_configuration_value(
            constants.SHOW_VALUE_BOUNDARY,
            constants.SHOW_VALUE_BOUNDARY_FALSE,
        )
        self.root.after_idle(self.hide_value_boundaries)

    def _show_value_boundaries(self):
        """Adjust settings to show value boundaries."""
        self._make_configuration().set_configuration_value(
            constants.SHOW_VALUE_BOUNDARY,
            constants.SHOW_VALUE_BOUNDARY_TRUE,
        )
        self.root.after_idle(self.show_value_boundaries)

    def hide_value_boundaries(self):
        """Display the widget content without value boundaries."""
        if self.content is None:
            return
        ranges = self.widget.tag_ranges(constants.UI_VALUE_BOUNDARY_TAG)
        if not ranges:
            return

        # The tkinter.Text.delete() method does not support multiple ranges
        # but the underlying tk.Text.delete() call does support them (as
        # stated in the Tcl/Tk text manual page).
        text_delete_ranges(self.widget, *ranges)

    def show_value_boundaries(self):
        """Display the widget content with value boundaries."""
        if self.content is None:
            return
        widget = self.widget
        if widget.tag_nextrange(constants.UI_VALUE_BOUNDARY_TAG, "1.0"):
            return
        boundary = constants.BOUNDARY
        boundary_tag = constants.UI_VALUE_BOUNDARY_TAG
        value_tag = constants.FIELD_VALUE_TAG
        mark = tkinter.END
        while True:
            mark = widget.mark_previous(mark)
            if not mark:
                break
            if not mark.startswith(value_tag):
                continue
            range_ = widget.tag_nextrange(value_tag, mark)
            if not range_:
                continue
            if widget.compare(widget.index(mark), "==", range_[0]):
                for index in reversed(range_):
                    widget.insert(index, boundary, boundary_tag)
                range_ = widget.tag_nextrange(value_tag, mark)
                widget.mark_set(mark, range_[0])

    def _accept_dump_as_valid(self):
        """Adjust settings to accept dump tags without any checks."""
        self._make_configuration().set_configuration_value(
            constants.CHECK_NAME_COUNT,
            constants.CHECK_NAME_COUNT_FALSE,
        )

    def _check_dump_name_counts(self):
        """Adjust settings to verify name tag count equals # char count."""
        self._make_configuration().set_configuration_value(
            constants.CHECK_NAME_COUNT,
            constants.CHECK_NAME_COUNT_TRUE,
        )

    def get_toplevel(self):
        """Return the toplevel widget."""
        return self.root

    def quit_edit(self):
        """Quit application, after confirmation if unsaved edits exist."""
        title = "Quit"
        if self.widget.edit_modified():
            if not tkinter.messagebox.askyesno(
                master=self.widget,
                message="".join(
                    (
                        "Text has been modified.\n\n",
                        "Do you wish to quit without saving edits?\n\n",
                        "Yes to quit without saving file.",
                    )
                ),
                title=title,
            ):
                return
        self.widget.winfo_toplevel().destroy()
        return

    def get_text_without_tag_bound(self):
        """Return text without bound tag from widget.

        The tag 'bound' indicates characters which are the boundaries of
        editable values.  These boundaries are not necessary; rather they
        are a visual aid for spotting editable areas.

        """
        # The 'displaychars' hack is preferred because anticipated future
        # development requires removal of characters tagged by at least two
        # different tags.  Inversion of the range cannot work in that case.

        # widget = self.widget
        # ranges = widget.tag_ranges(constants.UI_VALUE_BOUNDARY_TAG)
        # if not ranges:
        #     return widget.get("1.0", widget.index(tkinter.END))
        # ranges = ("1.0",) + ranges + (tkinter.END,)

        #  The tkinter.Text.get() method does not support multiple ranges
        #  but the underlying tk.Text.get() call does support them (as
        #  stated in the Tcl/Tk text manual page).
        #  (This hack probably belongs in solentware_misc.workarounds).
        # return "".join(widget.tk.call(widget._w, "get", *ranges))

        widget = self.widget
        widget.tag_configure(
            constants.UI_VALUE_BOUNDARY_TAG, elide=tkinter.TRUE
        )

        #  The tkinter.Text.get() method does not support the 'displaychars'
        #  option but the underlying tk.Text.get() call does support it (as
        #  stated in the Tcl/Tk text manual page).
        text = text_get_displaychars(widget, "1.0", tkinter.END)

        widget.tag_configure(
            constants.UI_VALUE_BOUNDARY_TAG, elide=tkinter.FALSE
        )
        return text

    def _start_hint(self, event=None):
        """Show a simple 'get started' message."""
        self._char_properties(event=event)

        # May be trying to invoke a menu option.
        if event.keysym == "Alt_L":
            return "break"

        tkinter.messagebox.showinfo(
            master=self.widget,
            message="".join(
                (
                    "Open a file or start a new one with menu option\n\n",
                    "'File | Open' or 'File | New'",
                )
            ),
            title="Quick Start",
        )
        return "break"

    @staticmethod
    def _make_configuration():
        """Return a configuration.Configuration instance."""
        return configuration.Configuration()

    @staticmethod
    def _show_value_boundary(conf):
        """Return True if configuration file SHOW_VALUE_BOUNDARY is true."""
        return bool(
            conf.get_configuration_value(constants.SHOW_VALUE_BOUNDARY)
            == constants.SHOW_VALUE_BOUNDARY_TRUE
        )

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

    def _inhibit_binding(self, inhibit):
        """Return True if self.widget has text tagged with a tag in inhibit."""
        for tag in inhibit:
            if self.widget.tag_ranges(tag):
                return True
        return False

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

    def _create_inserter(self):
        """Create the application's inserter instance.

        The inserter is an instance of inserter.Inserter class.

        Subclasses should override this method to create an instance of a
        suitable subclass of Inserter.

        """
        self._inserter = inserter.Inserter()

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

    def _value_range_containing_mark(self, index):
        """Return value range containing mark index or None."""
        widget = self.widget
        range_ = widget.tag_prevrange(constants.FIELD_VALUE_TAG, index)
        if (
            range_
            and widget.compare(range_[0], "<=", index)
            and widget.compare(range_[1], ">=", index)
        ):
            return range_
        range_ = widget.tag_nextrange(constants.FIELD_VALUE_TAG, index)
        if range_ and widget.compare(range_[0], "==", index):
            return range_
        return None

    def _value_range_containing_insert_mark(self):
        """Return value range containing insert mark or None."""
        return self._value_range_containing_mark(tkinter.INSERT)

    def _value_range_nearest_mark(self, index):
        """Return value range nearest mark index or None.

        Previous range is chosen as nearest before next range if insert
        mark is not within a value range.

        """
        widget = self.widget
        tag_names = widget.tag_names(index)
        for tag in tag_names:
            if tag == constants.FIELD_VALUE_TAG:
                return self._value_range_containing_mark(index)
        range_ = widget.tag_prevrange(constants.FIELD_VALUE_TAG, index)
        if range_:
            return range_
        range_ = widget.tag_nextrange(constants.FIELD_VALUE_TAG, index)
        if range_:
            return range_
        return None

    def _value_range_nearest_insert_mark(self):
        """Return value range nearest insert mark or None."""
        return self._value_range_nearest_mark(tkinter.INSERT)

    def _value_range_nearest_current_mark(self):
        """Return value range nearest curren mark or None."""
        return self._value_range_nearest_mark(tkinter.CURRENT)

    def _get_part_record_field_types_and_names_for_value(self, index):
        """Return tuple part and record types and names, and field type.

        index is assumed to be a location with the 'value' tag, which may
        not have an associated value nor any associated field instances.

        Format is (part-type, record-type, field-type, part-name, record-name).

        The names are the types with a numeric suffix.  The part, record, and
        field, type identifiers may be the same.

        """
        widget = self.widget
        value_names = set(widget.tag_names(index)).difference(
            constants.NON_RECORD_IDENTITY_TAG_NAMES
        )
        range_ = widget.tag_prevrange(constants.FIELD_NAME_TAG, index)
        if not range_:
            return None
        name_names = set(widget.tag_names(range_[0])).difference(
            constants.NON_RECORD_NAME_TAG_NAMES
        )
        part_names, insert_names = fields.get_identity_tags_for_names(
            widget, value_names.copy(), range_[0]
        )
        record_id = value_names.intersection(name_names).intersection(
            insert_names
        )
        part_id = record_id.intersection(part_names)
        record_id.difference_update(part_id)
        record = insert_names.difference(part_names)
        if not record:
            record = insert_names.difference(value_names)
            record.discard(constants.FIELD_NAME_TAG)
            record.discard(constants.UI_NAME_HIGHLIGHT_TAG)
            part = set(record)
        else:
            record = record.difference(value_names)
            record.discard(constants.UI_NAME_HIGHLIGHT_TAG)
            part = part_names.difference(insert_names)
        field = name_names.difference(insert_names)
        if not field:
            field = set(record)
        else:
            field = field.difference(value_names)
            field.discard(constants.FIELD_NAME_TAG)
        for item in (part_id, record, field, part):
            if len(item) != 1:
                return None
        part_id = part_id.pop()
        if record_id:
            record_id = record_id.pop()
        else:
            record_id = part_id
        part = part.pop()
        record = record.pop()
        siblings = self._get_existing_fields_in_record(part, record, record_id)
        return (part, record, field.pop(), part_id, record_id, siblings)

    def _get_bindings_context_after_up_or_down(self):
        """Set KeyPress and popup menu bindings for field at index."""
        return self._get_part_record_field_types_and_names_for_value(
            tkinter.INSERT
        )

    def _get_part_record_field_types_and_names_for_name(self, index):
        """Return tuple part and record types and names, and field type.

        index is assumed to be a location with the 'name' tag, which may
        not have an associated value nor any associated field instances.

        Format is (part-type, record-type, field-type, part-name, record-name).

        The names are the types with a numeric suffix.  The part, record, and
        field, type identifiers may be the same.

        """
        widget = self.widget
        tag_names = set(widget.tag_names(index))
        if constants.FIELD_NAME_TAG not in tag_names:
            return None
        tag_names.remove(constants.FIELD_NAME_TAG)
        part = tag_names.intersection(constants.PART_TAGS)
        if len(part) == 1:
            identity_tag_names = tag_names.difference(
                part.union(constants.NON_RECORD_NAME_TAG_NAMES)
            )
            # Need exactly one name for picking record_id and field, where
            # record_id will be part_id too.
            # In some badly constructed files there will be no names (a file
            # starting with a valid sequence of COLUMN, TABLE START, value,
            # and TABLE END, fields; followed by a valid OTHER RESULTS
            # sequence, and FINISH, fields for example).
            # Maybe it is possible to get more than two names.
            # Probably difficult to give a coherent explanation of field
            # traversal behaviour across all cases: but crashes are avoided
            # in what can reasonably described as random field sequences
            # compared with the expected field structure.
            if len(identity_tag_names) != 1:
                return None
            record_id = identity_tag_names.pop()
            part = part.pop()
            if part in constants.RECORD_TAGS:
                field = part
            else:
                field = None
            siblings = self._get_existing_fields_in_record(
                part, part, record_id
            )
            return (part, part, field, record_id, record_id, siblings)
        range_ = widget.tag_nextrange(constants.FIELD_VALUE_TAG, index)
        if not range_:
            return None
        return self._get_part_record_field_types_and_names_for_value(range_[0])

    def _get_existing_fields_in_record(self, part, record, record_id):
        """Return field names present in record."""
        names = set()
        widget = self.widget
        field_name_tag = constants.FIELD_NAME_TAG
        key = (part, record)
        if key not in self._allowed_inserts:
            return names
        allowed = self._allowed_inserts[key].union(record)
        index = "1.0"
        while True:
            range_ = widget.tag_nextrange(record_id, index)
            if not range_:
                break
            range_names = set(widget.tag_names(range_[0]))
            if field_name_tag not in range_names:
                index = range_[1]
                continue
            found = set()
            for name in range_names:
                if name in allowed:
                    found.add(name)
            found.discard(record)
            assert len(found) < 2
            names.update(found)
            index = range_[1]
        return names

    def _get_bindings_context_after_control_up_or_down(self):
        """Return KeyPress and popup menu bindings for field at index."""
        return self._get_part_record_field_types_and_names_for_name(
            tkinter.INSERT
        )

    def _get_bindings_context_after_buttonpress(self):
        """Return binding descriptions for field at current mark."""
        # Assume Double and Triple ButtonPress-1 events are disabled to
        # avoid false detection of a change in context.
        tag_names = set(self.widget.tag_names(tkinter.CURRENT))
        if tag_names.intersection(constants.FIELD_TAG_NAMES):
            return self._get_part_record_field_types_and_names_for_value(
                tkinter.CURRENT
            )
        return None

    # Should this be like 'after_buttonpress' or 'control_up_or_down'?
    def _get_bindings_context_at_insert_mark(self):
        """Return binding descriptions for field at insert mark."""
        tag_names = set(self.widget.tag_names(tkinter.INSERT))
        if constants.FIELD_NAME_TAG in tag_names:
            return self._get_part_record_field_types_and_names_for_name(
                tkinter.INSERT
            )
        if constants.FIELD_VALUE_TAG in tag_names:
            return self._get_part_record_field_types_and_names_for_value(
                tkinter.INSERT
            )
        return None

    def _define_scrolling_event_and_command_handlers(self, actions):
        """Define event and command handlers for widget navigation.

        The method names derived from actions must not duplicate names from
        sequences module.

        The two *_<derived name> methods are alternative ways of invoking
        the _handle_<derived name> method.

        """
        for item in actions:
            suffix = item[1]
            handler = "_handle_" + suffix
            assert hasattr(self, handler)
            self._define_event_handler(suffix, handler)
            self._define_command_handler(suffix, handler)

    # Diagnostic tool.
    @staticmethod
    def _show_keysym(event=None):
        """Show key."""
        print("@", event.keysym, event.keysym_num, event.state)

    # Diagnostic tool.
    def _show_tag_names_at_insert_tag(self):
        """Show names of tags of character at INSERT tag index."""
        widget = self.widget
        print(
            "#", widget.index(tkinter.INSERT), widget.tag_names(tkinter.INSERT)
        )

    # Diagnostic tool.
    def _char_properties(self, event):
        """Print index, char, and tags, at current pointer location."""
        # It is sometimes difficult to tell what tags a character has from
        # the *.tk_text_dump file.
        if event is not None and event.widget is not self.widget:
            return "break"
        widget = self.widget
        print(
            "%",
            widget.index(tkinter.CURRENT),
            repr(widget.get(tkinter.CURRENT)),
            widget.tag_names(tkinter.CURRENT),
            widget.index(tkinter.INSERT),
            event.keysym if event is not None else event,
        )
        return None
