# submission.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file editor."""

import os
import tkinter
import ast

from ..core import constants
from ..core import sequences
from ..core import submission_inserter
from ..core import fields
from . import header
from .method_makers import define_sequence_insert_map_insert_methods

_RESULT_FIELDS = (
    constants.PIN1,
    constants.PIN2,
    constants.SCORE,
)

# Define scrolling events and commands.
_ACTIONS = (
    ("<Shift-KeyPress-Down>", "next_fieldset", "Next fieldset", "Shift-Down"),
    ("<Shift-KeyPress-Up>", "prior_fieldset", "Previous fieldset", "Shift-Up"),
    ("<Control-KeyPress-Up>", "prior_part", "Previous part", "Control-Up"),
    ("<Control-KeyPress-Down>", "next_part", "Next part", "Control-Down"),
)


class SubmissionError(Exception):
    """Exception class for submission module."""


class Submission(header.Header):
    """Define and use an ECF results submission file editor."""

    _TITLE_SUFFIX = "   <ECF results file>"
    _sequences = (sequences.HEADER_SEQUENCES, sequences.SUBMISSION_SEQUENCES)
    _allowed_inserts = {
        (
            constants.EVENT_DETAILS,
            constants.EVENT_DETAILS,
        ): constants.EVENT_DETAILS_FIELD_TAGS,
        (
            constants.PLAYER_LIST,
            constants.PLAYER_LIST,
        ): constants.PLAYER_LIST_FIELD_TAGS,
        (constants.PLAYER_LIST, constants.PIN): constants.PIN_FIELD_TAGS,
        (
            constants.MATCH_RESULTS,
            constants.MATCH_RESULTS,
        ): frozenset((constants.RESULTS_DATE, constants.WHITE_ON)),
        (
            constants.OTHER_RESULTS,
            constants.OTHER_RESULTS,
        ): frozenset((constants.WHITE_ON,)),
        (
            constants.SECTION_RESULTS,
            constants.SECTION_RESULTS,
        ): frozenset((constants.RESULTS_DATE, constants.WHITE_ON)),
        (
            constants.MATCH_RESULTS,
            constants.PIN1,
        ): constants.HPIN_MATCH_FIELD_TAGS,
        (
            constants.OTHER_RESULTS,
            constants.PIN1,
        ): constants.HPIN_OTHER_FIELD_TAGS,
        (
            constants.SECTION_RESULTS,
            constants.PIN1,
        ): constants.HPIN_SECTION_FIELD_TAGS,
        (constants.FINISH, constants.FINISH): frozenset(),
    }

    def _define_scrolling_methods(self):
        """Define methods for scrolling."""
        super()._define_scrolling_methods()
        self._define_scrolling_event_and_command_handlers(_ACTIONS)

    def _add_scrolling_commands_to_popup_menu(self):
        """Delegate then set commands for scrolling."""
        super()._add_scrolling_commands_to_popup_menu()
        for item in _ACTIONS:
            command = getattr(self, "_command_" + item[1])
            self._scroll_menu.add_command(
                label=item[2], command=command, accelerator=item[3]
            )

    def _get_next_fieldset_range(self, index):
        """Return first range after index with an identity tag not at index."""
        widget = self.widget
        names = set(widget.tag_names(index))
        names.difference_update(constants.NON_RECORD_IDENTITY_TAG_NAMES)
        while True:
            range_ = widget.tag_nextrange(constants.FIELD_NAME_TAG, index)
            if not range_:
                return range_
            range_names = set(widget.tag_names(range_[0]))
            range_names.difference_update(
                constants.NON_RECORD_IDENTITY_TAG_NAMES.union(names)
            )
            if range_names:
                index = range_[0]
                break
            index = range_[1]
        return widget.tag_nextrange(constants.FIELD_NAME_TAG, index)

    def _set_insert_mark_at_first_value_in_next_fieldset(self):
        """Set tkinter.INSERT at first value in next fieldset ranges."""
        widget = self.widget
        end = "1.0"
        index = widget.index(tkinter.INSERT)
        range_ = self._get_next_fieldset_range(index)
        while True:
            if not range_:
                if index == end:
                    return
                index = end
                range_ = self._get_next_fieldset_range(index)
                continue
            mark = widget.mark_next(range_[0])
            while True:
                if mark is None or mark.startswith(constants.FIELD_VALUE_TAG):
                    break
                mark = widget.mark_next(mark)
            if mark is None:
                if index == end:
                    return
                index = end
                range_ = self._get_next_fieldset_range(index)
                continue
            break
        widget.mark_set(tkinter.INSERT, widget.index(mark))
        self._set_colours_and_see(tkinter.INSERT)
        return

    def _get_next_part_range(self, index):
        """Return first range after index with an identity tag not at index."""
        widget = self.widget
        while True:
            range_ = widget.tag_nextrange(constants.FIELD_NAME_TAG, index)
            if not range_:
                return range_
            names = set(widget.tag_names(index))
            if names.intersection(constants.ERROR_TAG_NAMES):
                index = range_[-1]
                continue
            names.difference_update(constants.NON_RECORD_IDENTITY_TAG_NAMES)
            if not names:
                index = range_[0]
                break
            names = set(widget.tag_names(range_[0]))
            names.difference_update(constants.NON_RECORD_IDENTITY_TAG_NAMES)
            index = fields.get_part_and_fieldset_range_starts(
                widget, names, next_=False
            )[-1]
            break
        return widget.tag_nextrange(constants.FIELD_NAME_TAG, index)

    def _set_insert_mark_at_first_field_in_next_part(self):
        """Set tkinter.INSERT at first name in next part identity ranges.

        This is needed to allow positioning the insert mark at the end of
        a part field, such as PLAYER LIST, which does not have a value
        component, by keypress actions.

        """
        widget = self.widget
        end = "1.0"
        index = widget.index(tkinter.INSERT)
        range_ = self._get_next_part_range(index)
        while True:
            if not range_:
                if index == end:
                    return
                index = end
                range_ = self._get_next_part_range(index)
                continue
            widget.mark_set(tkinter.INSERT, range_[0])
            break
        context = self._get_bindings_context_after_control_up_or_down()
        self._set_bindings_context_and_ensure_visible(context)
        return

    def _handle_next_fieldset(self):
        """Handle next fieldset event."""
        self._set_insert_mark_at_first_value_in_next_fieldset()

    def _handle_next_part(self):
        """Handle next part event."""
        self._set_insert_mark_at_first_field_in_next_part()

    def _get_prior_fieldset_range(self, index):
        """Return last range before index with an identity tag not at index."""
        widget = self.widget
        names = set(widget.tag_names(index))
        names.difference_update(constants.NON_RECORD_IDENTITY_TAG_NAMES)
        while True:
            range_ = widget.tag_prevrange(constants.FIELD_NAME_TAG, index)
            if not range_:
                return range_
            range_names = set(widget.tag_names(range_[0]))
            range_names.difference_update(
                constants.NON_RECORD_IDENTITY_TAG_NAMES
            )
            if len(range_names) == 1:
                index = widget.tag_nextrange(range_names.pop(), "1.0")[0]
                break
            range_names.difference_update(
                constants.NON_RECORD_IDENTITY_TAG_NAMES
            )

            # Step over locations without any identity tags.
            # Should be equivalent to locations with an ERROR_TAG_NAMES tag,
            # which are included in NON_RECORD_IDENTITY_TAG_NAMES.
            # Alternative is to include fields tagged with an ERROR_TAG_NAMES
            # tag in the current identity tags, which is the idea about to be
            # implemented.
            if not range_names:
                index = range_[0]
                continue

            prior_range_names = range_names.difference(names)
            if len(prior_range_names) == 1:
                index = widget.tag_nextrange(prior_range_names.pop(), "1.0")[0]
                break
            pr1 = widget.tag_nextrange(range_names.pop(), "1.0")[0]
            pr2 = widget.tag_nextrange(range_names.pop(), "1.0")[0]
            if range_names:
                raise SubmissionError("Too many tag names to pick fieldset")
            if widget.compare(pr1, ">", pr2):
                index = pr1
            else:
                index = pr2
            break
        return widget.tag_nextrange(constants.FIELD_NAME_TAG, index)

    def _set_insert_mark_at_first_value_in_prior_fieldset(self):
        """Set tkinter.INSERT at first value in prior fieldset ranges."""
        widget = self.widget
        end = widget.index(tkinter.END)
        index = widget.index(tkinter.INSERT)
        range_ = self._get_prior_fieldset_range(index)
        while True:
            if not range_:
                if index == end:
                    return
                index = end
                range_ = self._get_prior_fieldset_range(index)
                continue
            mark = widget.mark_next(range_[0])
            while True:
                if mark is None or mark.startswith(constants.FIELD_VALUE_TAG):
                    break
                mark = widget.mark_next(mark)
            if mark is None:
                if index == end:
                    return
                index = end
                range_ = self._get_prior_fieldset_range(index)
                continue
            if widget.compare(widget.index(mark), ">=", index):
                range_ = self._get_prior_fieldset_range(range_[0])
                continue
            break
        widget.mark_set(tkinter.INSERT, widget.index(mark))
        self._set_colours_and_see(tkinter.INSERT)
        return

    def _get_prior_part_range(self, index):
        """Return last range before index with an identity tag not at index."""
        widget = self.widget
        names = set(widget.tag_names(index))
        names.difference_update(constants.NON_RECORD_IDENTITY_TAG_NAMES)
        while True:
            range_ = widget.tag_prevrange(constants.FIELD_NAME_TAG, index)
            if not range_:
                break
            if not names:
                index = range_[0]
                break
            names = set(widget.tag_names(range_[0]))
            names.difference_update(constants.NON_RECORD_IDENTITY_TAG_NAMES)

            # Step over locations without any identity tags.
            # Should be equivalent to locations with an ERROR_TAG_NAMES tag,
            # which are included in NON_RECORD_IDENTITY_TAG_NAMES.
            # Alternative is to include fields tagged with an ERROR_TAG_NAMES
            # tag in the current identity tags, which is the idea about to be
            # implemented.
            if not names:
                index = range_[0]
                continue

            index = fields.get_part_and_fieldset_range_starts(
                widget, names, next_=True
            )[0]
            break
        return widget.tag_nextrange(constants.FIELD_NAME_TAG, index)

    def _set_insert_mark_at_first_field_in_prior_part(self):
        """Set tkinter.INSERT at first name in prior part identity ranges.

        This is needed to allow positioning the insert mark at the end of
        a part field, such as PLAYER LIST, which does not have a value
        component, by keypress actions.

        """
        widget = self.widget
        end = widget.index(tkinter.END)
        index = widget.index(tkinter.INSERT)
        range_ = self._get_prior_part_range(index)
        while True:
            if not range_:
                if index == end:
                    return
                index = end
                range_ = self._get_prior_part_range(index)
                continue
            widget.mark_set(tkinter.INSERT, range_[0])
            break
        context = self._get_bindings_context_after_control_up_or_down()
        self._set_bindings_context_and_ensure_visible(context)
        return

    def _handle_prior_fieldset(self):
        """Handle previous fieldset menu action."""
        self._set_insert_mark_at_first_value_in_prior_fieldset()

    def _handle_prior_part(self):
        """Handle previous part menu action."""
        self._set_insert_mark_at_first_field_in_prior_part()

    def _bind_events_file_open(self):
        """Delegate then set fieldset and part navigation bindings."""
        super()._bind_events_file_open()
        widget = self.widget
        for item in _ACTIONS:
            function = getattr(self, "_keypress_" + item[1])
            self.bind(widget, item[0], function=function)

    def _bind_events_file_not_open(self):
        """Delegate then unset fieldset and part navigation bindings."""
        super()._bind_events_file_not_open()
        widget = self.widget
        self.bind(widget, "<Shift-KeyPress-Down>")
        self.bind(widget, "<Shift-KeyPress-Up>")
        self.bind(widget, "<Control-KeyPress-Up>")
        self.bind(widget, "<Control-KeyPress-Down>")

    def _create_inserter(self):
        """Create the application's inserter instance.

        The inserter is an instance of submission_inserter.SubmissionInserter
        class.

        Subclasses should override this method to create an instance of a
        suitable subclass of SubmissionInserter.

        """
        self._inserter = submission_inserter.SubmissionInserter()

    def _handle_finish(self):
        """Insert FINISH after later of last 'name' and 'value' tag ranges.

        The definition of field implies tkinter.END is always the insertion
        point: assuming any '#<any string>' is at worst an unknown field
        name.

        """
        if self.widget.tag_ranges(constants.FINISH):
            tkinter.messagebox.showinfo(message="FINISH field already present")
            return
        self._inserter.insert_finish(self.widget, self.content)

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

        The caller is expected to save changes to both <filename>.txt and
        <filename>.tk_text_dump.

        """
        name, ext = os.path.splitext(filename)
        if ext not in (self._TK_TEXT_DUMP_EXT, self._RSF_EXT):
            for extension in (self._TK_TEXT_DUMP_EXT, self._RSF_EXT):
                if os.path.isfile(name + extension):
                    tkinter.messagebox.showinfo(
                        master=self.widget,
                        message="".join(
                            (
                                "Cannot open\n\n",
                                name,
                                "\n\nbecause\n\n",
                                name + extension,
                                "\n\nexists",
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
            dumpname = name + self._TK_TEXT_DUMP_EXT
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
                                "Cannot show\n\n",
                                name,
                                "\n\ncontent because a data format ",
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
            textname = name + self._RSF_EXT
            if os.path.isfile(textname):
                with open(textname, mode="r", encoding=self.encoding) as inp:
                    text = inp.read()
            else:
                text = None
            if dump is not None and text is not None:
                if text_without_tag_elide != text:
                    tkinter.messagebox.showinfo(
                        master=self.widget,
                        message="".join(
                            (
                                "Cannot open\n\n",
                                name,
                                "\n\nbecause the text from the ",
                                self._TK_TEXT_DUMP_EXT,
                                " and ",
                                self._RSF_EXT,
                                " files is different\n\n",
                                "(changing one of the names will allow both ",
                                "to be opened and saved as text to be ",
                                "compared)",
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

    def _save_file(self, filename):
        """Save widget text and dump in *.txt and *.tk_text_dump files."""
        # The attempt to lose the trailing newline in the widget.get() and
        # widget.dump() calls by expressing their index2 arguments as
        # widget.index(tkinter.END + "-1c") fails because it also loses the
        # final tagoff entries in the dump.
        # The builder.Builder.parse() method has to compensate by stripping
        # trailing newlines.  The parser.Parser.parse() method does not.
        super()._save_file(os.path.splitext(filename)[0] + self._RSF_EXT)
        with open(
            os.path.splitext(filename)[0] + self._TK_TEXT_DUMP_EXT,
            mode="w",
            encoding=self.encoding,
        ) as file:
            file.write(
                repr(self.widget.dump("1.0", self.widget.index(tkinter.END)))
            )


define_sequence_insert_map_insert_methods(
    class_=Submission,
    map_=submission_inserter.sequence_insert_map,
    sequence=sequences.SUBMISSION_SEQUENCES,
)
del define_sequence_insert_map_insert_methods
