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
from solentware_misc.gui import bindings

from . import help_
from .. import APPLICATION_NAME
from ..core import constants
from ..core import configuration
from ..core import fields
from ..core import sequences

STARTUP_MINIMUM_WIDTH = 800
STARTUP_MINIMUM_HEIGHT = 400


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


class Editor(bindings.Bindings):
    """Define menus and text widget for ECF results submission file editor."""

    encoding = "utf-8"
    _TITLE_SUFFIX = ""
    _sequences = ()
    _allowed_inserts = {}
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
        self.content = None
        self._define_event_and_command_handlers()

    def _create_menubar_menus(self):
        """Create the menus for application.

        Subclasses should override this method to create their menubar.

        """

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
            for index in reversed(range_):
                widget.insert(index, boundary, boundary_tag)

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
