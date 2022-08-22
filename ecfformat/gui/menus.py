# menus.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file editor framework and menus."""

import os
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
from ..core import content
from ..core import configuration
from ..core import taggedcontent
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


class Menus(bindings.Bindings):
    """Define menus and text widget for ECF results submission file editor."""

    encoding = "utf-8"
    _TITLE_SUFFIX = ""
    _sequences = ()
    _allowed_inserts = {}
    _NEW_FILE_TEXT = "\n".join(
        (
            "#EVENT DETAILS",
        )
    )
    _RSF_EXT = ".txt"
    _RSF_PATTERN = "*" + _RSF_EXT
    _RSF_TYPE = "ECF results submission file"
    _TK_TEXT_DUMP_EXT = ".tk_text_dump"
    _NO_VALUE_TAGS = None

    def __init__(
        self,
        application_name=APPLICATION_NAME,
        width=None,
        height=None,
        use_toplevel=False,
        **kargs,
    ):
        """Create the file and GUI objects.

        **kargs - passed to tkinter Toplevel widget if use_toplevel True

        """
        super().__init__()
        self.application_name = application_name
        if use_toplevel:
            root = tkinter.Toplevel(**kargs)
        else:
            root = tkinter.Tk()
        if width is None:
            width = STARTUP_MINIMUM_WIDTH
        if height is None:
            height = STARTUP_MINIMUM_HEIGHT
        self.root = root
        self.filename = None
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
        """Create the menus for application."""
        menubar = tkinter.Menu(master=self.root)
        menu1 = tkinter.Menu(master=menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=menu1, underline=0)
        menu1.add_command(
            label="Open",
            underline=0,
            command=self.try_command(self.file_open, menu1),
        )
        menu1.add_command(
            label="Close",
            underline=0,
            command=self.try_command(self.close_file, menu1),
        )
        menu1.add_separator()
        menu1.add_command(
            label="Save",
            underline=0,
            command=self.try_command(self.save_file, menu1),
        )
        menu1.add_command(
            label="Save As",
            underline=5,
            command=self.try_command(self.save_file_as, menu1),
        )
        menu1.add_command(
            label="Save Copy As",
            underline=3,
            command=self.try_command(self.save_file_copy_as, menu1),
        )
        menu1.add_separator()
        menu1.add_command(
            label="New",
            underline=0,
            command=self.try_command(self.file_new, menu1),
        )
        menu1.add_separator()
        menu1.add_command(
            label="Quit",
            underline=0,
            command=self.try_command(self.quit_edit, menu1),
        )
        menu2 = tkinter.Menu(master=menubar, tearoff=False)
        menubar.add_cascade(label="Settings", menu=menu2, underline=0)
        menu21 = tkinter.Menu(master=menu2, tearoff=False)
        menu2.add_cascade(label="Value Boundary", menu=menu21, underline=0)
        menu21.add_command(
            label="Hide",
            underline=0,
            command=self.try_command(self._hide_value_boundaries, menu21),
        )
        menu21.add_command(
            label="Show",
            underline=0,
            command=self.try_command(self._show_value_boundaries, menu21),
        )
        menu22 = tkinter.Menu(master=menu2, tearoff=False)
        menu2.add_cascade(label="Field Counts", menu=menu22, underline=0)
        menu22.add_command(
            label="Accept",
            underline=0,
            command=self.try_command(self._accept_dump_as_valid, menu22),
        )
        menu22.add_command(
            label="Validate",
            underline=0,
            command=self.try_command(self._check_dump_name_counts, menu22),
        )
        menuhelp = tkinter.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", menu=menuhelp, underline=0)
        menuhelp.add_command(
            label="Guide",
            underline=0,
            command=self.try_command(self.help_guide, menuhelp),
        )
        menuhelp.add_command(
            label="Reference",
            underline=0,
            command=self.try_command(self.help_keyboard, menuhelp),
        )
        menuhelp.add_command(
            label="About",
            underline=0,
            command=self.try_command(self.help_about, menuhelp),
        )
        self.root.configure(menu=menubar)

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

    def close_file(self):
        """Close file if confirmed in dialogue."""
        if self.widget.edit_modified():
            message = "".join(
                (
                    "Text has been modified.\n\n",
                    "Do you wish to save edits before closing file?",
                    " (Yes / No)\n\nCancel to abandon closing file.",
                )
            )
            title = "Close"
            dlg = tkinter.messagebox.askyesnocancel(
                master=self.widget, message=message, title=title
            )
            if dlg is None:
                return
            if dlg:
                if isinstance(self.filename, str):
                    self._save_file(self.filename)
                elif not self._save_file_as(title=title):
                    if not tkinter.messagebox.askyesno(
                        master=self.widget,
                        message="".join(
                            (
                                "Modified text has not been saved.\n\n",
                                "Do you wish to close file?",
                            )
                        ),
                        title=title,
                    ):
                        return
        self.widget.delete("1.0", tkinter.END)
        self.widget.edit_modified(tkinter.FALSE)
        self.filename = None
        self.widget.winfo_toplevel().wm_title(self.set_title_suffix(None))
        return

    def file_open(self):
        """Open file and populate widget with content."""
        title = "Open file"
        if self.widget.edit_modified():
            message = "".join(
                (
                    "Text has been modified.\n\n",
                    "Do you wish to save edits before opening a file?",
                    " (Yes / No)\n\nCancel to abandon opening file.",
                )
            )
            dlg = tkinter.messagebox.askyesnocancel(
                master=self.widget,
                message=message,
                title=title,
            )
            if dlg is None:
                return
            if dlg:
                if isinstance(self.filename, str):
                    self._save_file(self.filename)
                elif not self._save_file_as(title="Save current before Open"):
                    if not tkinter.messagebox.askyesno(
                        master=self.widget,
                        message="".join(
                            (
                                "Modified text has not been saved.\n\n",
                                "Do you wish to open file?",
                            )
                        ),
                        title=title,
                    ):
                        return
        conf = self._make_configuration()
        filename = tkinter.filedialog.askopenfilename(
            parent=self.widget,
            title=title,
            filetypes=(
                (self._RSF_TYPE, self._RSF_PATTERN),
                ("All files", "*"),
            ),
            initialdir=conf.get_configuration_value(
                constants.RECENT_RESULTS_FORMAT_FILE
            ),
        )
        if not filename:
            return
        name, text, dump = self._get_text_and_filename_without_extension(
            filename, title
        )
        if name is None:
            return
        conf.set_configuration_value(
            constants.RECENT_RESULTS_FORMAT_FILE,
            conf.convert_home_directory_to_tilde(os.path.dirname(filename)),
        )
        self.widget.delete("1.0", tkinter.END)
        show_boundary = self._show_value_boundary(conf)
        if dump is None:
            parser = content.Content(text, show_boundary, self._NO_VALUE_TAGS)
        else:
            parser = taggedcontent.TaggedContent(
                dump, show_boundary, self._NO_VALUE_TAGS
            )
        self.content = parser.parse(self.widget, stop_at=None)
        if self.content.fields_message is not None:
            tkinter.messagebox.showinfo(
                master=self.widget,
                message=self.content.fields_message,
                title=title,
            )
        self.filename = name + self._RSF_EXT
        self.widget.winfo_toplevel().wm_title(self.set_title_suffix(filename))
        self.widget.edit_modified(tkinter.FALSE)
        return

    def file_new(self):
        """Populate widget with default content for new file."""
        title = "New file"
        if self.widget.edit_modified():
            message = "".join(
                (
                    "Text has been modified.\n\n",
                    "Do you wish to save edits before opening new file?",
                    " (Yes / No)\n\nCancel to abandon new file.",
                )
            )
            dlg = tkinter.messagebox.askyesnocancel(
                master=self.widget,
                message=message,
                title=title,
            )
            if dlg is None:
                return
            if dlg:
                if isinstance(self.filename, str):
                    self._save_file(self.filename)
                elif not self._save_file_as(title="Save current before New"):
                    if not tkinter.messagebox.askyesno(
                        master=self.widget,
                        message="".join(
                            (
                                "Modified text has not been saved.\n\n",
                                "Do you wish to start new file?",
                            )
                        ),
                        title=title,
                    ):
                        return
        self.widget.delete("1.0", tkinter.END)
        conf = self._make_configuration()
        parser = content.Content(
            self._NEW_FILE_TEXT,
            self._show_value_boundary(conf),
            self._NO_VALUE_TAGS,
        )
        self.content = parser.parse(self.widget, stop_at=None)
        self.filename = True
        self.widget.winfo_toplevel().wm_title(self.set_title_suffix("New"))
        self.widget.edit_modified(tkinter.FALSE)
        return

    def _get_text_and_filename_without_extension(self, filename, title):
        """Return content of *.txt and *.tk_text_dump variants of filename.

        Attempts to open <filename>.<other ext> are not allowed if either
        <filename>.txt or <filename>.tk_text_dump exist.  When neither
        exist <filename>.<other ext> is opened and treated as the .txt
        version.

        Attempts to open <filename>.tk_text_dump are rejected.

        Attempts to open <filename>.txt when <filename>.tk_text_dump exists
        are accepted even though the caller is expected to save changes to
        <filename>.txt only.

        """
        name, ext = os.path.splitext(filename)
        if ext not in (self._RSF_EXT,):
            for extension in (self._RSF_EXT, self._TK_TEXT_DUMP_EXT):
                if os.path.isfile(name + extension):
                    if ext == self._TK_TEXT_DUMP_EXT:
                        tkinter.messagebox.showinfo(
                            master=self.widget,
                            message="".join(
                                (
                                    "Opening\n\n",
                                    name + ext,
                                    "\n\nis not allowed because changes ",
                                    " would not be saved to both\n\n",
                                    name + ext,
                                    "\n\nand\n\n",
                                    name + self._RSF_EXT,
                                    "\n\nbut you can open the latter file",
                                )
                            ),
                            title=title,
                        )
                        return (None, False, False)

                    # Expressed this way to avoid pylint duplicate-code
                    # report for the message argument.
                    # See method in submission module with same name.
                    tkinter.messagebox.showinfo(
                        master=self.widget,
                        message=(name + ext).join(
                            (
                                "Cannot open\n\n",
                                (name + extension).join(
                                    (
                                        "\n\nbecause\n\n",
                                        "\n\nexists",
                                    )
                                ),
                            )
                        ),
                        title=title,
                    )

                    return (None, False, False)
            with open(filename, mode="r", encoding=self.encoding) as inp:
                text = inp.read()
        else:
            textname = name + self._RSF_EXT
            if os.path.isfile(textname):
                if os.path.isfile(name + self._TK_TEXT_DUMP_EXT):
                    tkinter.messagebox.showinfo(
                        master=self.widget,
                        message="".join(
                            (
                                "Any changes made to\n\n",
                                textname,
                                "\n\nwill not be saved to\n\n",
                                name + self._TK_TEXT_DUMP_EXT,
                                "\n\nas well",
                            )
                        ),
                        title=title,
                    )
                with open(textname, mode="r", encoding=self.encoding) as inp:
                    text = inp.read()
            else:
                text = None
        return (name, text, None)

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

    def save_file(self):
        """Save *.txt and *.tk_text_dump files for widget."""
        title = "Save File"
        widget = self.widget
        if not self.filename:
            tkinter.messagebox.showinfo(
                master=self.widget,
                message="There is no file open to save",
                title=title,
            )
            return
        if not isinstance(self.filename, str):
            sfa = self._save_file_as(title=title)
            if sfa:
                self.filename = sfa
                widget.winfo_toplevel().wm_title(
                    self.set_title_suffix(self.filename)
                )
                widget.edit_modified(tkinter.FALSE)
            return
        dlg = tkinter.messagebox.askyesno(
            master=widget,
            message="".join(("Please confirm Save action",)),
            title=title,
        )
        if dlg:
            conf = self._make_configuration()
            self._save_file(self.filename)
            conf.set_configuration_value(
                constants.RECENT_RESULTS_FORMAT_FILE,
                conf.convert_home_directory_to_tilde(
                    os.path.dirname(self.filename)
                ),
            )
            widget.edit_modified(tkinter.FALSE)

    def save_file_as(self):
        """Save file and set self.filename to name of file saved to."""
        filename = self._save_file_as()
        if isinstance(filename, str):
            self.filename = filename
            self.widget.winfo_toplevel().wm_title(
                self.set_title_suffix(filename)
            )
            self.widget.edit_modified(tkinter.FALSE)

    def save_file_copy_as(self):
        """Save file without updating self.filename."""
        self._save_file_as(title="Save Copy As")

    def _save_file_as(self, title="Save As"):
        """Return True if widget *.txt and *.tk_text_dump files are saved."""
        widget = self.widget
        conf = self._make_configuration()
        filename = tkinter.filedialog.asksaveasfilename(
            parent=widget,
            title=title,
            defaultextension=self._RSF_EXT,
            filetypes=(
                ("All files", "*"),
                (self._RSF_TYPE, self._RSF_PATTERN),
            ),
            initialdir=conf.get_configuration_value(
                constants.RECENT_RESULTS_FORMAT_FILE
            ),
        )
        if filename:
            self._save_file(filename)
            conf.set_configuration_value(
                constants.RECENT_RESULTS_FORMAT_FILE,
                conf.convert_home_directory_to_tilde(
                    os.path.dirname(filename)
                ),
            )
            return filename
        return False

    def _save_file(self, filename):
        """Save widget text and dump in *.txt and *.tk_text_dump files."""
        # The attempt to lose the trailing newline in the widget.get() and
        # widget.dump() calls by expressing their index2 arguments as
        # widget.index(tkinter.END + "-1c") fails because it also loses the
        # final tagoff entries in the dump.
        # The builder.Builder.parse() method has to compensate by stripping
        # trailing newlines.  The parser.Parser.parse() method does not.
        with open(filename, mode="w", encoding=self.encoding) as file:
            file.write(self.get_text_without_tag_bound())

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


define_sequence_insert_map_insert_methods(class_=Menus)
