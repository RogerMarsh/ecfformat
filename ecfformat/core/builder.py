# builder.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Build field structure of ECF results submission file from tagged content."""

import tkinter
import re

from . import constants
from . import fields
from . import configuration

# Each item in a tk Text dump has three elements: key, value, and index.
DUMP_ITEM_LENGTH = 3

# The valid keys (from Tk Built-In Commands text manual page).
# The image and window keys are tolerated as legal Text widget state.
# The mark key is accepted as internal state of the Text widget.
# The text, tagon, and tagoff, keys are validated and used to build the
# ECF result submission file structure.
TK_TEXT_DUMP_KEYS = frozenset(
    (
        constants.TK_TEXT_DUMP_TEXT,
        constants.TK_TEXT_DUMP_MARK,
        constants.TK_TEXT_DUMP_TAGON,
        constants.TK_TEXT_DUMP_TAGOFF,
        constants.TK_TEXT_DUMP_IMAGE,
        constants.TK_TEXT_DUMP_WINDOW,
    )
)
TK_TEXT_DUMP_TAG_KEYS = frozenset(
    (
        constants.TK_TEXT_DUMP_TAGON,
        constants.TK_TEXT_DUMP_TAGOFF,
    )
)

index_re = re.compile(r"[1-9][0-9]*\.[0-9]*")
tag_re = re.compile(r"^([a-zA-Z]+)(?:[1-9](?:[0-9])*)*$")


class BuilderError(Exception):
    """Exception class for builder module."""


class Builder:
    """Build field structure of ECF results submission file from tk Text dump.

    An event header must have one of each field in event_details, and is
    allowed more than one of each field in event_details_at_least_one.

    An event header must have exactly one of each field in one of the sets
    from each of environments and time_limits.  Note this means the
    ENVIRONMENT field is optional and it's value defaults to 'OTB'.

    The ECF ignores the fields in event_details_ignored, but these are
    accepted in submissions for historical reasons (in other words they
    were used at some time in the past).

    """

    def __init__(self, dump, value_edge):
        """Initialise the data structure."""
        self.fields = fields.FieldsFromDump(dump, value_edge)
        self.tag_edges = {
            constants.TK_TEXT_DUMP_TAGON: [],
            constants.TK_TEXT_DUMP_TAGOFF: [],
        }
        self._fatal_error = None

    def parse_dump(self, widget, stop_at=constants.EVENT_DETAILS):
        """Split text into fields and validate field structure.

        widget provides the index compare method: it's content is not
        changed.

        stop_at is the field name at which parsing will stop.  By default
        only the first field is expected to be parsed because it should be
        the EVENT DETAILS field.

        """
        non_record_identity_tag_names = constants.NON_RECORD_IDENTITY_TAG_NAMES
        most_recent_index = "1.0"
        for item in self.fields.document:
            if len(item) != DUMP_ITEM_LENGTH:
                self.fields.fields_message = "".join(
                    (
                        "Item length is ",
                        str(len(item)),
                        ": it must be ",
                        DUMP_ITEM_LENGTH,
                        " in a tk Text dump file",
                    )
                )
                self._fatal_error = True
                break
            key, value, index = item
            if key not in TK_TEXT_DUMP_KEYS:  # Is key ok.
                self.fields.fields_message = "".join(
                    (
                        "Key '",
                        key,
                        "' is not expected in a tk Text dump file",
                    )
                )
                self._fatal_error = True
                break
            if index_re.match(index) is None:  # index looks like a float()
                self.fields.fields_message = "".join(
                    (
                        "Index '",
                        index,
                        "' is not in expected format in a tk Text dump file",
                    )
                )
                self._fatal_error = True
                break
            if widget.compare(
                widget.index(most_recent_index),
                ">",
                widget.index(index),
            ):
                self.fields.fields_message = "".join(
                    (
                        "Index '",
                        index,
                        "' compares 'less than' previous index '",
                        most_recent_index,
                        "': not allowed in a tk Text dump file",
                    )
                )
                self._fatal_error = True
                break
            most_recent_index = index
            if key in TK_TEXT_DUMP_TAG_KEYS:
                match = tag_re.match(value)
                if match is None:
                    if self._fatal_error is None:
                        self.fields.fields_message = "".join(
                            (
                                "Field name '",
                                value,
                                "' not expected in a tk Text dump file ",
                                "for an ECF results submission",
                            )
                        )
                        self._fatal_error = False
                elif match.group(1) not in non_record_identity_tag_names:
                    if self._fatal_error is None:
                        self.fields.fields_message = "".join(
                            (
                                "Field name '",
                                value,
                                "' not expected in a tk Text dump file ",
                                "for an ECF results submission\n\n",
                                "(Value in badly structured ",
                                "TABLE perhaps?)",
                            )
                        )
                        self._fatal_error = False
                if value == constants.FIELD_NAME_TAG:
                    self.tag_edges[key].append(index)
            if key == constants.TK_TEXT_DUMP_TEXT and value == stop_at:
                break

    def parse(self, widget, stop_at=constants.EVENT_DETAILS):
        """Delegate to parse_dump then populate widget if content ok."""
        self.parse_dump(widget, stop_at=stop_at)
        if self.fields.fields_message is not None:
            if self._fatal_error:
                return self.fields
        text = self.fields.text_getter()

        # Insert text into widget and apply tags from tk Text dump file.
        # Set the tag suffix elements and *_tag attributes in self.fields
        # from the tags present in the tk Text dump file.
        # The trailing "\n" was not stripped from the widget.get() call
        # when saving the file, to preserve compatibility with dump() call
        # to keep final tagoff elements.  Remove it here because the Text
        # widget adds a trailing newline on next get() call.
        # The parser.Parser.parse() method can and does use a different
        # strategy to apply tags which incidentally avoids the trailing
        # newline problem.
        widget.insert("1.0", text.rstrip("\n"))
        tags = {}
        marks = []
        marks_set = set()
        for key, value, index in self.fields.document:
            if key == constants.TK_TEXT_DUMP_TAGON:
                if value in tags:
                    self.fields.fields_message = "".join(
                        (
                            "tagon for field '",
                            value,
                            "' found at index '",
                            index,
                            "' after prior tagon without matching tagoff",
                        )
                    )
                    self._fatal_error = True
                    break
                tags[value] = index
                self.fields.note_high_suffix_for_tag(value)
                continue
            if key == constants.TK_TEXT_DUMP_TAGOFF:
                if value not in tags:
                    self.fields.fields_message = "".join(
                        (
                            "tagoff for field '",
                            value,
                            "' found at index '",
                            index,
                            "' without a prior matching tagon",
                        )
                    )
                    self._fatal_error = True
                    break
                widget.tag_add(value, tags[value], index)
                del tags[value]
                continue
            if key == constants.TK_TEXT_DUMP_MARK:
                if key in marks_set:
                    self.fields.fields_message = "".join(
                        (
                            "Attempt to set mark '",
                            value,
                            "' found at index '",
                            index,
                            "' but mark is already set",
                        )
                    )
                    self._fatal_error = True
                    break
                marks_set.add(value)
                marks.append((value, index))
                continue
        for value, index in marks:
            widget.mark_set(value, index)
        self._verify_field_count(widget)
        return self.fields

    def _verify_field_count(self, widget):
        """Report mismatch between field count and '#' character count."""
        if (
            configuration.Configuration().get_configuration_value(
                constants.CHECK_NAME_COUNT
            )
            == constants.CHECK_NAME_COUNT_TRUE
        ):
            if widget.get("1.0", tkinter.END).count(
                constants.FIELD_SEPARATOR
            ) != len(self.tag_edges[constants.TK_TEXT_DUMP_TAGON]):
                if self._fatal_error is None:
                    self.fields.fields_message = "".join(
                        (
                            "Count of '",
                            constants.FIELD_SEPARATOR,
                            "' characters is not equal the ",
                            "number of field names (TABLEs used perhaps?)",
                        )
                    )

    @property
    def is_valid_result_submission_format(self):
        """Return True if self.text has a valid field structure."""
        return not self._fatal_error
