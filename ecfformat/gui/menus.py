# menus.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file editor framework and menus."""

import os
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import ast

from . import bindings
from . import help_
from .. import APPLICATION_NAME
from ..core import constants
from ..core import content
from ..core import configuration
from ..core import taggedcontent
from ..core import sequences

STARTUP_MINIMUM_WIDTH = 800
STARTUP_MINIMUM_HEIGHT = 400
TK_TEXT_DUMP_EXT = ".tk_text_dump"
TEXT_EXT = ".txt"


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
        configuration.Configuration().set_configuration_value(
            constants.SHOW_VALUE_BOUNDARY,
            constants.SHOW_VALUE_BOUNDARY_FALSE,
        )
        self.root.after_idle(self.hide_value_boundaries)

    def _show_value_boundaries(self):
        """Adjust settings to show value boundaries."""
        configuration.Configuration().set_configuration_value(
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
        # (This hack probably belongs in solentware_misc.workarounds).
        self.widget.tk.call(self.widget._w, "delete", *ranges)

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

    @staticmethod
    def _accept_dump_as_valid():
        """Adjust settings to accept dump tags without any checks."""
        configuration.Configuration().set_configuration_value(
            constants.CHECK_NAME_COUNT,
            constants.CHECK_NAME_COUNT_FALSE,
        )

    @staticmethod
    def _check_dump_name_counts():
        """Adjust settings to verify name tag count equals # char count."""
        configuration.Configuration().set_configuration_value(
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
                    "(Yes / No)\nCancel to abandon closing file.",
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
                    "(Yes / No)\nCancel to abandon opening file.",
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
        conf = configuration.Configuration()
        filename = tkinter.filedialog.askopenfilename(
            parent=self.widget,
            title=title,
            filetypes=(
                ("ECF results submission file", "*.txt"),
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
        show_boundary = bool(
            conf.get_configuration_value(constants.SHOW_VALUE_BOUNDARY)
            == constants.SHOW_VALUE_BOUNDARY_TRUE
        )
        if dump is None:
            parser = content.Content(text, show_boundary)
        else:
            parser = taggedcontent.TaggedContent(dump, show_boundary)
        self.content = parser.parse(self.widget, stop_at=None)
        if self.content.fields_message is not None:
            tkinter.messagebox.showinfo(
                master=self.widget,
                message=self.content.fields_message,
                title=title,
            )
        self.filename = name + TEXT_EXT
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
                    "(Yes / No)\nCancel to abandon new file.",
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
        conf = configuration.Configuration()
        parser = content.Content(
            "\n".join(
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
            ),
            bool(
                conf.get_configuration_value(constants.SHOW_VALUE_BOUNDARY)
                == constants.SHOW_VALUE_BOUNDARY_TRUE
            ),
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

        If <filename>.tk_text_dump exists it is used, even if the .txt file
        exists and is selected, because it has tagging information saved
        when the file was previously closed.

        If both <filename>.tk_text_dump and <filename>.txt exist the file
        is presented only if their text content is the same.

        """
        name, ext = os.path.splitext(filename)
        if ext not in (TK_TEXT_DUMP_EXT, TEXT_EXT):
            for extension in (TK_TEXT_DUMP_EXT, TEXT_EXT):
                if os.path.isfile(name + extension):
                    tkinter.messagebox.showinfo(
                        master=self.widget,
                        message="".join(
                            (
                                "Cannot open '",
                                name,
                                "' because '",
                                name + extension + "' exists",
                            )
                        ),
                        title=title,
                    )
                    return (None, False, False)
            dumptext = None
            dump = None
            with open(filename, mode="r", encoding=self.encoding) as inp:
                text = inp.read()
        else:
            dumpname = name + TK_TEXT_DUMP_EXT
            if os.path.isfile(dumpname):
                with open(dumpname, mode="r", encoding=self.encoding) as inp:
                    filestring = inp.read()
                try:
                    dump = ast.literal_eval(filestring)
                except SyntaxError:
                    tkinter.messagebox.showinfo(
                        master=self.widget,
                        message="".join(
                            (
                                "Cannot show '",
                                name,
                                "' content because a data format ",
                                " problem was found",
                            )
                        ),
                        title=title,
                    )
                    return (None, False, False)
                (
                    dumptext,
                    text_without_tag_elide,
                ) = self._get_text_without_tag_elide(dump)
            else:
                dump = None
                dumptext = None
            textname = name + TEXT_EXT
            if os.path.isfile(textname):
                with open(textname, mode="r", encoding=self.encoding) as inp:
                    text = inp.read()
            else:
                text = None
            if dump is not None and text is not None:
                if text_without_tag_elide != text:
                    tkinter.messagebox.showinfo(
                        master=self.widget,
                        message=" ".join(
                            (
                                "Cannot open '",
                                name,
                                "' because text from '",
                                TK_TEXT_DUMP_EXT,
                                "' and '",
                                TEXT_EXT,
                                "' files is diferrent",
                            )
                        ),
                        title=title,
                    )
                    return (None, False, False)
        return (name, text if dumptext is None else dumptext, dump)

    @staticmethod
    def _get_text_without_tag_elide(dump):
        """Return text from dump ignoring text with tag 'elided'."""
        ui_bound_tag = constants.UI_VALUE_BOUNDARY_TAG
        ttd_text = constants.TK_TEXT_DUMP_TEXT
        ttd_tagon = constants.TK_TEXT_DUMP_TAGON
        ttd_tagoff = constants.TK_TEXT_DUMP_TAGOFF
        dumptext = "".join(e[1] for e in dump if e[0] == ttd_text)
        text_without_tag_elide = []
        elide = False
        for item in dump:
            if item[0] == ttd_text and not elide:
                text_without_tag_elide.append(item[1])
            elif item[1] == ui_bound_tag:
                if item[0] == ttd_tagon:
                    elide = True
                elif item[0] == ttd_tagoff:
                    elide = False
        return dumptext, "".join(text_without_tag_elide)

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
            conf = configuration.Configuration()
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
        conf = configuration.Configuration()
        filename = tkinter.filedialog.asksaveasfilename(
            parent=widget,
            title=title,
            defaultextension=".txt",
            filetypes=(
                ("All files", "*"),
                ("ECF results submission file", "*.txt"),
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
        with open(
            os.path.splitext(filename)[0] + TEXT_EXT,
            mode="w",
            encoding=self.encoding,
        ) as file:
            file.write(self.get_text_without_tag_bound())
        with open(
            os.path.splitext(filename)[0] + TK_TEXT_DUMP_EXT,
            mode="w",
            encoding=self.encoding,
        ) as file:
            file.write(
                repr(self.widget.dump("1.0", self.widget.index(tkinter.END)))
            )

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
        #  (This hack probably belongs in solentware_misc.workarounds).
        text = "".join(
            widget.tk.call(
                widget._w, "get", "-displaychars", "1.0", tkinter.END
            )
        )

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
