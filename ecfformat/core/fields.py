# fields.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""The fields derived from the text of an ECF results submission file."""

import tkinter
import re

from . import constants

# The tag names, without spaces, are mapped to field names with spaces.
# The field names are upper case with spaces as listed in the specification
# from the ECF, although the ECF ignores case and spaces in field names.
tag_to_name = {
    constants.BCF_CODE: constants.NAME_BCF_CODE,
    constants.BCF_NO: constants.NAME_BCF_NO,
    constants.CLUB_CODE: constants.NAME_CLUB_CODE,
    constants.CLUB_COUNTY: constants.NAME_CLUB_COUNTY,
    constants.CLUB_NAME: constants.NAME_CLUB_NAME,
    constants.COMMENT_LIST: constants.NAME_COMMENT,
    constants.COMMENT_PIN: constants.NAME_COMMENT,
    constants.DATE_OF_BIRTH: constants.NAME_DATE_OF_BIRTH,
    constants.ECF_CODE: constants.NAME_ECF_CODE,
    constants.ECF_NO: constants.NAME_ECF_NO,
    constants.EVENT_CODE: constants.NAME_EVENT_CODE,
    constants.EVENT_DATE: constants.NAME_EVENT_DATE,
    constants.EVENT_DETAILS: constants.NAME_EVENT_DETAILS,
    constants.EVENT_NAME: constants.NAME_EVENT_NAME,
    constants.FIDE_NO: constants.NAME_FIDE_NO,
    constants.FINAL_RESULT_DATE: constants.NAME_FINAL_RESULT_DATE,
    constants.GAME_DATE: constants.NAME_GAME_DATE,
    constants.INFORM_FIDE: constants.NAME_INFORM_FIDE,
    constants.INFORM_CHESSMOVES: constants.NAME_INFORM_CHESSMOVES,
    constants.INFORM_GRAND_PRIX: constants.NAME_INFORM_GRAND_PRIX,
    constants.INFORM_UNION: constants.NAME_INFORM_UNION,
    constants.MATCH_RESULTS: constants.NAME_MATCH_RESULTS,
    constants.MINUTES_FIRST_SESSION: constants.NAME_MINUTES_FIRST_SESSION,
    constants.MINUTES_FOR_GAME: constants.NAME_MINUTES_FOR_GAME,
    constants.MINUTES_REST_OF_GAME: constants.NAME_MINUTES_REST_OF_GAME,
    constants.MINUTES_SECOND_SESSION: constants.NAME_MINUTES_SECOND_SESSION,
    constants.MOVES_FIRST_SESSION: constants.NAME_MOVES_FIRST_SESSION,
    constants.MOVES_SECOND_SESSION: constants.NAME_MOVES_SECOND_SESSION,
    constants.OTHER_RESULTS: constants.NAME_OTHER_RESULTS,
    constants.PLAYER_LIST: constants.NAME_PLAYER_LIST,
    constants.PIN1: constants.NAME_PIN1,
    constants.PIN2: constants.NAME_PIN2,
    constants.RESULTS_DATE: constants.NAME_RESULTS_DATE,
    constants.RESULTS_DUPLICATED: constants.NAME_RESULTS_DUPLICATED,
    constants.RESULTS_OFFICER: constants.NAME_RESULTS_OFFICER,
    constants.RESULTS_OFFICER_ADDRESS: constants.NAME_RESULTS_OFFICER_ADDRESS,
    constants.SECONDS_PER_MOVE: constants.NAME_SECONDS_PER_MOVE,
    constants.SECTION_RESULTS: constants.NAME_SECTION_RESULTS,
    constants.SUBMISSION_INDEX: constants.NAME_SUBMISSION_INDEX,
    constants.TABLE_START: constants.NAME_TABLE_START,
    constants.TABLE_END: constants.NAME_TABLE_END,
    constants.TREASURER_ADDRESS: constants.NAME_TREASURER_ADDRESS,
    constants.WHITE_ON: constants.NAME_WHITE_ON,
}
SUFFIX_INCREMENT_NAMES = constants.PART_TAGS.union(constants.SUBPART_TAGS)
# Still unclear if SUBPART_SUBTAGS should include COMMENT.
SUBPART_SUBTAGS = (
    constants.PIN_FIELD_TAGS.union(constants.HPIN_MATCH_FIELD_TAGS)
    .union(constants.HPIN_OTHER_FIELD_TAGS)
    .union(constants.HPIN_SECTION_FIELD_TAGS)
    .difference(constants.PLAYER_LIST_FIELD_TAGS)
)
# The allowed field sets insertable just before s2 when insertion point is
# between s1 and s2.  All field set insertion points are tagged with one
# of the START_* tags.
# None neans no pre- or post- tag.
_DETAILS = (constants.EVENT_DETAILS,)
_PIN = (constants.PIN,)
_LIST = (constants.PLAYER_LIST,)
_LIST_FINISH = (constants.PLAYER_LIST, constants.FINISH)
_PLAYERS = (
    constants.PIN,
    constants.MATCH_RESULTS,
    constants.OTHER_RESULTS,
    constants.SECTION_RESULTS,
)
_PLAYERS_FINISH = (
    constants.PIN,
    constants.MATCH_RESULTS,
    constants.OTHER_RESULTS,
    constants.SECTION_RESULTS,
    constants.FINISH,
)
_RESULTS = (
    constants.PIN1,
    constants.MATCH_RESULTS,
    constants.OTHER_RESULTS,
    constants.SECTION_RESULTS,
)
_RESULTS_FINISH = (
    constants.PIN1,
    constants.MATCH_RESULTS,
    constants.OTHER_RESULTS,
    constants.SECTION_RESULTS,
    constants.FINISH,
)
_SECTIONS = (
    constants.MATCH_RESULTS,
    constants.OTHER_RESULTS,
    constants.SECTION_RESULTS,
)
tag_context_to_insert_map = {
    (None, None): _DETAILS,
    (None, constants.EVENT_DETAILS): (),
    (None, constants.PLAYER_LIST): _DETAILS,
    (None, constants.PIN): _DETAILS,
    (None, constants.PIN1): _DETAILS,
    (None, constants.FINISH): _DETAILS,
    (constants.EVENT_DETAILS, None): _LIST_FINISH,
    (constants.EVENT_DETAILS, constants.FINISH): _LIST,
    (constants.EVENT_DETAILS, constants.PLAYER_LIST): (),
    (constants.EVENT_DETAILS, constants.PIN1): _LIST,
    (constants.EVENT_DETAILS, constants.PIN): _LIST,
    (constants.PLAYER_LIST, None): _PLAYERS_FINISH,
    (constants.PLAYER_LIST, constants.PIN): _PIN,
    (constants.PLAYER_LIST, constants.FINISH): _PLAYERS_FINISH,
    (constants.PLAYER_LIST, constants.PIN1): _SECTIONS,
    (constants.PIN, constants.PIN): _PIN,
    (constants.PIN, None): _PLAYERS_FINISH,
    (constants.PIN, constants.FINISH): _PLAYERS,
    (constants.PIN, constants.PIN1): _SECTIONS,
    (constants.PIN1, None): _RESULTS_FINISH,
    (constants.PIN1, constants.PIN1): _RESULTS,
    (constants.PIN1, constants.FINISH): _RESULTS,
}
del _DETAILS
del _PIN
del _LIST
del _LIST_FINISH
del _PLAYERS
del _PLAYERS_FINISH
del _RESULTS
del _RESULTS_FINISH
del _SECTIONS

# These fields exist as "#name#" not "#name=value#".
FIELDS_WITHOUT_VALUE = frozenset(
    (
        constants.EVENT_DETAILS,
        constants.FINISH,
        constants.INFORM_FIDE,
        constants.INFORM_CHESSMOVES,
        constants.INFORM_GRAND_PRIX,
        constants.INFORM_UNION,
        constants.PLAYER_LIST,
        constants.RESULTS_DUPLICATED,
        constants.TABLE_START,
        constants.TABLE_END,
    )
)

suffixed_tag_re = re.compile(
    "|".join(key for key in SUFFIX_INCREMENT_NAMES).join(
        (r"^(", r")([1-9][0-9]*)$")
    )
)
record_tag_re = re.compile(r"^[^0-9]+[0-9]+$")


class FieldsError(Exception):
    """Exception class for fields module."""


class NoIdentityTagsError(Exception):
    """Exception raised attempting to find range for empty name set.

    This is known to occur when there is text before the first '#' and the
    field name immediately after the first '#' does not start a part.

    If this field name is 'EVENT DETAILS', for example, a part is started
    and appropriate identity tags are set without searching for identity
    tags set previously.

    """


class TooManyTagsError(Exception):
    """Exception raised attempting to find part and fieldset tag names.

    At most two tag names should remain after the tags describing a field
    are removed.

    The descriptive tags say if the text is a field name or value, or is
    some kind of error, or control user interface properties such as
    selection and highlighting.

    """


class Fields:
    """The items derived from text in an ECF results submission file.

    items contains, after removing leading and trailing whitespace:

    ('',) tuples, for '##' sequences.
    (<name>,) tuples for '#<name>#' sequences like '#FINISH#'.
    (<name>,<value>) tuples for '#<name>=<value>#' sequences like '#PIN=1#'.

    tags contains tuples of tuples of tag names for the TAGS feature of
    tkinter.Text widgets as implemented by the Tcl/Tk version supporting
    tkinter.  The tags element corresponding to a (<name>,<value>) element
    in items has two tuples.  The items element for a '##' sequence is
    ('',) so the tags element can be defined with one tuple (and be
    consistent with the rest).

    The EVENT DETAILS, FINISH, PLAYER LIST, MATCH RESULTS, OTHER RESULTS,
    and SECTION RESULTS, names delimit the parts of an ECF results
    submission file.  The three RESULTS parts can repeat as many times as
    necessary.  The PLAYER LIST has sub-parts delimited by the PIN name.
    The three RESULTS parts have sub-parts delimited by the PIN1 name.
    The sub-parts can repeat as many times as necessary.

    Each item is tagged for it's part, and sub-part if it is in one, and
    with a tag for it's own name.  Tags for repeatable names get a suffix
    to distinguish one from another.

    The '#' and '=' delimiters get their own tags shared by all occurrences
    and get associated with items by relative location.

    The two repeatable items in the EVENT DETAILS part; TREASURER ADDRESS,
    and RESULTS OFFICER ADDRESS, do not have a unique suffix because they
    do not have sub-parts.

    """

    def __init__(self, value_edge, no_value_tags):
        """Initialise the data structure."""
        self.tag_suffix = {}
        for key in SUFFIX_INCREMENT_NAMES:
            self.tag_suffix[key] = 0
        self._fields_message = None
        self.value_edge = value_edge
        self.error_tag = None
        self.value_mark_suffix = 0
        if no_value_tags is None:
            self.no_value_tags = frozenset()
        else:
            self.no_value_tags = frozenset(no_value_tags)

    def text_getter(self):
        """Override this method in subclasses and return a str."""
        raise NotImplementedError("Fields.text_getter()")

    @property
    def fields_message(self):
        """Return error message, or None if no error message set."""
        return self._fields_message

    @fields_message.setter
    def fields_message(self, value):
        """Set error message."""
        if isinstance(value, str):
            self._fields_message = value
        else:
            self._fields_message = "Non-str message"

    def insert_tagged_char_at_mark(self, widget, char):
        """Insert char in widget at a value mark and tag it as a value."""
        tag_names = [
            tag
            for tag in widget.tag_names(
                widget.tag_prevrange(constants.FIELD_NAME_TAG, tkinter.INSERT)[
                    0
                ]
            )
            if record_tag_re.match(tag) is not None
        ] + [constants.FIELD_VALUE_TAG, constants.UI_VALUE_HIGHLIGHT_TAG]
        if not self.value_edge:
            widget.insert(tkinter.INSERT, char, tag_names)
            return
        # Include all marks at INSERT index in search for next_ mark.
        start = widget.index(tkinter.INSERT)
        next_ = self.get_next_mark_after_start(widget, start)
        widget.insert(
            tkinter.INSERT,
            constants.BOUNDARY,
            constants.UI_VALUE_BOUNDARY_TAG,
        )
        # next_ mark will be set to current INSERT index after inserting
        # char and boundary.
        start = widget.index(tkinter.INSERT)
        widget.insert(tkinter.INSERT, char, tag_names)
        # INSERT mark will be set to current INSERT index after inserting
        # boundary.
        end = widget.index(tkinter.INSERT)
        widget.insert(
            tkinter.INSERT,
            constants.BOUNDARY,
            constants.UI_VALUE_BOUNDARY_TAG,
        )
        widget.mark_set(next_, start)
        widget.mark_set(tkinter.INSERT, end)

    @staticmethod
    def get_next_mark_after_start(widget, start):
        """Return next mark after start in widget."""
        while True:
            start = widget.mark_next(start)
            if not start:
                break
            if start.startswith(constants.FIELD_VALUE_TAG):
                break
        return start

    def _insert_name_value(self, widget, name, value, status):
        """Generate tag suffix and append name, value, and tags to items.

        status is expected to be 'ok', and error tag name, or None.

        None implies some or all the identity tag names at the insert point
        are not those required for the new field with name and value.

        """
        part_names, fieldset_names = get_identity_tags_for_index(widget)
        if status == constants.STATUS_OK:
            if name in SUFFIX_INCREMENT_NAMES:
                self.tag_suffix[name] += 1
                if name in constants.PART_TAGS:
                    field_tags = (name + str(self.tag_suffix[name]),)
                else:
                    subpart_tag = name + str(self.tag_suffix[name])
                    part_tag = (
                        part_names.intersection(fieldset_names)
                        .difference(constants.TAG_NAMES)
                        .pop()
                    )
                    field_tags = (part_tag, subpart_tag)
            elif name in SUBPART_SUBTAGS:
                field_tags = tuple(
                    fieldset_names.difference(constants.TAG_NAMES)
                )
                # unexpected's are appearing here so the asserts are wrong.
                # assert len(field_tags) == 2
                # assert len(part_names.intersection(fieldset_names)) == 1
                # assert len(fieldset_names) > len(part_names)
            else:
                field_tags = tuple(
                    part_names.intersection(fieldset_names).difference(
                        constants.TAG_NAMES
                    )
                )
                assert len(field_tags) == 1
        elif status in constants.ERROR_TAG_NAMES:
            field_tags = tuple(
                part_names.union(fieldset_names)
                .difference(constants.NON_RECORD_IDENTITY_TAG_NAMES)
                .union((status,))
            )
        else:
            field_tags = self.get_identity_tags_for_new_field(
                name, part_names, fieldset_names
            )
        self.insert_and_tag_name_value_into_document(
            widget, field_tags, name, value
        )

    def insert_name_value(self, widget, name, *args):
        """Insert newline if needed by name, delegate to _insert_name_value."""
        if name is None or name in constants.TAGS_START_NEWLINE:
            widget.insert(tkinter.INSERT, "\n")
        self._insert_name_value(widget, name, *args)

    def insert_name_value_without_newline_prefix(self, *args):
        """Delegate to _insert_name_value."""
        self._insert_name_value(*args)

    def append_table(self, widget, table):
        """Insert table items and tag them to fit table status."""
        try:
            if bool(len(table.values) % len(table.column_names)):
                status = constants.TAG_ERROR_TABLE_LAYOUT
            else:
                status = constants.STATUS_OK
        except ZeroDivisionError:
            table.set_column_definition_is_broken()
        if table.broken_column_definition:
            status = constants.TAG_ERROR_TABLE_LAYOUT
        for name, value in table.translate_table_to_name_value_pairs():
            self.insert_name_value(widget, name, value, status)

    # Check header.Header._insert_tagged_char_at_mark when modifying this
    # method: pylint spotted similarities which matter.
    def insert_and_tag_name_value_into_document(
        self, widget, tags, name, value
    ):
        """Insert text into widget and apply tags.

        name is None when the tabular structure has to be presented as a table
        because of some problem translating to 'name=value' format: usually
        the number of values is not an integer multiple of the number of
        columns.

        """
        # Not sure if eliding is necessary or desirable yet.
        # The things which could be elided will have known field names which
        # are not in the ECF Results Submission Format.
        # start_not_elided = widget.index(tkinter.INSERT)
        widget.insert(tkinter.INSERT, constants.FIELD_SEPARATOR)

        if name:
            start = widget.index(tkinter.INSERT)

            # Convert the tag name in name to it's field name for display
            # in the text widget.
            text_name = tag_to_name.get(name, name)
            widget.insert(tkinter.INSERT, text_name)

            end = widget.index(tkinter.INSERT)
            widget.tag_add(constants.FIELD_NAME_TAG, start, end)
            if constants.ERROR_TAG_NAMES not in tags:
                widget.tag_add(name, start, end)
            for tag in tags:
                widget.tag_add(tag, start, end)
        if value is None:
            return
        if name is not None:
            widget.insert(tkinter.INSERT, constants.NAME_VALUE_SEPARATOR, tags)
        start_value = widget.index(tkinter.INSERT)
        if name not in self.no_value_tags:
            self.value_mark_suffix += 1
            mark_name = constants.FIELD_VALUE_TAG + str(self.value_mark_suffix)
            widget.mark_set(mark_name, start_value)
            widget.mark_gravity(mark_name, tkinter.LEFT)
        if value:
            start = start_value
            if self.value_edge:
                widget.insert(
                    start,
                    constants.BOUNDARY,
                    constants.UI_VALUE_BOUNDARY_TAG,
                )
                start_value = widget.index(tkinter.INSERT)
                start = start_value
            if name not in self.no_value_tags:
                widget.insert(tkinter.INSERT, value, constants.FIELD_VALUE_TAG)
            else:
                widget.insert(tkinter.INSERT, value)
            end = widget.index(tkinter.INSERT)
            for tag in tags:
                widget.tag_add(tag, start, end)
            if self.value_edge:
                widget.insert(
                    end, constants.BOUNDARY, constants.UI_VALUE_BOUNDARY_TAG
                )
        return

    def _get_new_part_identity_tags(self, name, part_names, fieldset_names):
        """Return part and fieldset tag names for new part field."""
        del part_names, fieldset_names
        self.tag_suffix[name] += 1
        return (name, name + str(self.tag_suffix[name]))

    def _get_new_record_identity_tags(self, name, part_names, fieldset_names):
        """Return part and fieldset tag names for new record field."""
        self.tag_suffix[name] += 1
        return (
            name,
            name + str(self.tag_suffix[name]),
            part_names.intersection(fieldset_names)
            .difference(SUFFIX_INCREMENT_NAMES)
            .pop(),
        )

    # self_ not self to avoid pylint warning W0211 for self in static method.
    # Method is default in <dict>.get(...) in get_identity_tags_for_new_field
    # where the first argument is self passed explicitly.
    # Alternative is to make this a module function?
    @staticmethod
    def _get_context_identity_tags(self_, name, part_names, fieldset_names):
        """Return part and fieldset tag names for current context."""
        del self_, name
        return tuple(
            part_names.union(fieldset_names).difference(
                constants.NON_RECORD_IDENTITY_TAG_NAMES
            )
        )

    _new_identity_tags = {
        constants.EVENT_DETAILS: _get_new_part_identity_tags,
        constants.FINISH: _get_new_part_identity_tags,
        constants.MATCH_RESULTS: _get_new_part_identity_tags,
        constants.PLAYER_LIST: _get_new_part_identity_tags,
        constants.OTHER_RESULTS: _get_new_part_identity_tags,
        constants.SECTION_RESULTS: _get_new_part_identity_tags,
        constants.PIN: _get_new_record_identity_tags,
        constants.PIN1: _get_new_record_identity_tags,
    }

    def get_identity_tags_for_new_field(self, name, *args):
        """Return part and fieldset tag names for name."""
        return self._new_identity_tags.get(
            name, self._get_context_identity_tags
        )(self, name, *args)


class FieldsFromText(Fields):
    """Customise Fields to fit return value of tkinter Text get() call."""

    def __init__(self, document, *args):
        """Extend to validate text from an ECF results submission file.

        The original document from a text file is held in self._text_document.

        """
        super().__init__(*args)
        self._text_document = document

    @property
    def document(self):
        """Return self._text_document."""
        return self._text_document

    def text_getter(self):
        """Return text provided from file when instance was created.

        The file is expected to have been saved with the return value from
        a tkinter Text get("1.0", tkinter.END) call.

        """
        return self._text_document


class FieldsFromDump(Fields):
    """Customise Fields to fit return value of tkinter Text dump() call."""

    def __init__(self, document, *args):
        """Extend to validate text rebuilt from saved Text dump() call.

        The original document from a file containing tk Text dump output is
        held in self._dump_document.

        """
        super().__init__(*args)
        self._dump_document = document

    @property
    def document(self):
        """Return self._dump_document."""
        return self._dump_document

    def text_getter(self):
        """Return text provided from file when instance was created.

        The file is expected to have been saved with the repr(return value)
        from a tkinter Text dump("1.0", tkinter.END) call.

        """
        text = constants.TK_TEXT_DUMP_TEXT
        return "".join(e[1] for e in self._dump_document if e[0] == text)

    def note_high_suffix_for_tag(self, tag):
        """Update tag suffix dict with highest used numeric suffix for tag."""
        match = suffixed_tag_re.match(tag)
        if match is not None:
            key, suffix = match.group(1, 2)
            suffix = int(suffix)
            if suffix > self.tag_suffix[key]:
                self.tag_suffix[key] = suffix


def _null_part_and_fieldset():
    """Return 2-tuple of empty sets for null part and fieldset names.

    This is the part and fieldset context for locations before first '#'
    in text.

    """
    return (set(), set())


def get_part_and_fieldset_range_starts(widget, names, next_=True):
    """Return start of part and fieldset ranges for field tagged names.

    names is a set of tag names containing exactly one part identity tag
    and one fieldset identity tag.

    A part can be it's own fieldset for some or all fields allowed in the
    part, and contain other fieldsets after the fields in the part's own
    fieldset.

    Raise NoIdentityTagsError exception if no tag names are available for
    selecting the part and fieldset tag names from which the range starts
    are taken.

    Raise TooManyTagsError exception if more than two tag names are
    available for selecting the part and fieldset tag names from which the
    range starts are taken.

    The fieldset starts no earlier than the part, and ends no later than
    the part.

    bool(next_) == True causes the search  to be done by the tkinter.Text
    tag_prevrange command starting at location "1.0".  This is the default.

    bool(next_) == False causes the search to be done by the tkinter.Text
    tag_prevrange command starting at location tkinter.END.

    """
    if next_:
        range_step = widget.tag_nextrange
        index = "1.0"
        offset = 0
    else:
        range_step = widget.tag_prevrange
        index = tkinter.END
        offset = -1
    if not names:
        raise NoIdentityTagsError("No identity tag for field")
    if len(names) > 1:
        if len(names) > 2:
            raise FieldsError("Too many identity tags for field")
        range1 = range_step(names.pop(), index)
        range2 = range_step(names.pop(), index)
    else:
        range1 = range_step(names.pop(), index)
        range2 = range1
    if widget.compare(range1[0], ">", range2[0]):
        return (range2[offset], range1[offset])
    if widget.compare(range1[0], "<", range2[0]):
        return (range1[offset], range2[offset])
    if widget.compare(range1[1], ">", range2[1]):
        return (range2[offset], range1[offset])
    if widget.compare(range1[1], "<", range2[1]):
        return (range1[offset], range2[offset])
    return (range1[offset], range1[offset])


def get_identity_tags_for_names(widget, names, index):
    """Return part and fieldset tag names for index."""
    if not names:
        names = set(widget.tag_names(index)).difference(
            constants.NON_RECORD_IDENTITY_TAG_NAMES
        )
    if not names:
        return _null_part_and_fieldset()
    part_index, fieldset_index = get_part_and_fieldset_range_starts(
        widget, names, next_=True
    )
    return (
        set(widget.tag_names(part_index)).difference(
            constants.NON_RECORD_NAME_TAG_NAMES
        ),
        set(widget.tag_names(fieldset_index)).difference(
            constants.NON_RECORD_NAME_TAG_NAMES
        ),
    )


def get_identity_tags_for_index(widget, index=tkinter.INSERT, next_=True):
    """Return nearest part and fieldset identity tag names to index.

    index defaults to the tkinter.INSERT mark.

    See get_part_and_fieldset_range_starts for next_ argument description.

    """
    while True:
        names_range = widget.tag_prevrange(constants.FIELD_NAME_TAG, index)
        if not names_range:
            return _null_part_and_fieldset()
        names = set(widget.tag_names(names_range[0]))
        if names.intersection(constants.ERROR_TAG_NAMES):
            index = names_range[0]
            continue
        names.difference_update(constants.NON_RECORD_IDENTITY_TAG_NAMES)
        if not names:
            return _null_part_and_fieldset()
        break
    part_index, fieldset_index = get_part_and_fieldset_range_starts(
        widget, names, next_=next_
    )
    return (
        set(widget.tag_names(part_index)).difference(
            constants.NON_RECORD_NAME_TAG_NAMES
        ),
        set(widget.tag_names(fieldset_index)).difference(
            constants.NON_RECORD_NAME_TAG_NAMES
        ),
    )
