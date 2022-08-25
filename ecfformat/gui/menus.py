# menus.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file editor framework and menus."""

import os
import tkinter
import tkinter.messagebox
import tkinter.filedialog

from . import editor
from . import method_makers
from ..core import constants
from ..core import content
from ..core import configuration
from ..core import taggedcontent


class Menus(editor.Editor):
    """Define menus and text widget for ECF results submission file editor."""

    _NEW_FILE_TEXT = "\n".join(("#EVENT DETAILS",))
    _RSF_EXT = ".txt"
    _RSF_PATTERN = "*" + _RSF_EXT
    _RSF_TYPE = "ECF results submission file"
    _TK_TEXT_DUMP_EXT = ".tk_text_dump"

    def __init__(
        self,
        use_toplevel=False,
        application_name="",
        **kargs,
    ):
        """Create the file and GUI objects.

        **kargs - passed to tkinter Toplevel widget if use_toplevel True

        """
        if use_toplevel:
            root = tkinter.Toplevel(**kargs)
        else:
            root = tkinter.Tk()
        super().__init__(root=root, application_name=application_name, **kargs)
        self.filename = None

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

    @staticmethod
    def _make_configuration():
        """Return a configuration.Configuration instance."""
        return configuration.Configuration()


method_makers.define_sequence_insert_map_insert_methods(class_=Menus)
