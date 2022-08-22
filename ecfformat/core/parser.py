# parser.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Parse ECF results submission file to validate field structure."""

import tkinter
import re

from . import constants
from . import table
from . import fields
from . import expectedfields

# Most tag names are derived by converting input values to upper case and
# removing whitespace.  Some tag names are abbreviated, or mangled to avoid
# ambiguity in tags derived by appending digit sufficies.
no_whitespace_name_to_short_tag_name = {
    "".join(constants.NAME_EVENT_DETAILS.split()): constants.EVENT_DETAILS,
    "".join(constants.NAME_MATCH_RESULTS.split()): constants.MATCH_RESULTS,
    "".join(constants.NAME_OTHER_RESULTS.split()): constants.OTHER_RESULTS,
    "".join(constants.NAME_PLAYER_LIST.split()): constants.PLAYER_LIST,
    "".join(constants.NAME_SECTION_RESULTS.split()): constants.SECTION_RESULTS,
    constants.NAME_PIN1: constants.PIN1,
    constants.NAME_PIN2: constants.PIN2,
}
record_type_name_to_short_tag_name = {
    constants.NAME_MATCH_RESULTS: constants.MATCH_RESULTS,
    constants.NAME_OTHER_RESULTS: constants.OTHER_RESULTS,
    constants.NAME_PLAYER_LIST: constants.PLAYER_LIST,
    constants.NAME_SECTION_RESULTS: constants.SECTION_RESULTS,
}
column_name_to_short_tag_name = {
    constants.NAME_MATCH_RESULTS: constants.MATCH_RESULTS,
    constants.NAME_OTHER_RESULTS: constants.OTHER_RESULTS,
    constants.NAME_PLAYER_LIST: constants.PLAYER_LIST,
    constants.NAME_SECTION_RESULTS: constants.SECTION_RESULTS,
    constants.NAME_PIN1: constants.PIN1,
    constants.NAME_PIN2: constants.PIN2,
    constants.NAME_GAME_DATE: constants.GAME_DATE,
    constants.NAME_ECF_CODE: constants.ECF_CODE,
    constants.NAME_DATE_OF_BIRTH: constants.DATE_OF_BIRTH,
    constants.NAME_CLUB_CODE: constants.CLUB_CODE,
    constants.NAME_CLUB_NAME: constants.CLUB_NAME,
    constants.NAME_CLUB_COUNTY: constants.CLUB_COUNTY,
    constants.NAME_ECF_NO: constants.ECF_NO,
    constants.NAME_FIDE_NO: constants.FIDE_NO,
    constants.NAME_BCF_CODE: constants.BCF_CODE,
    constants.NAME_BCF_NO: constants.BCF_NO,
}
field_re = re.compile(r"#([^#]*)|([^#]*)")
_NAME_VALUE_SEPARATOR = constants.NAME_VALUE_SEPARATOR


class FieldTooLongError(Exception):
    """Value or unknown field name too long."""


class FieldStatusError(Exception):
    """Unknown status for field."""


class FirstFieldStatusError(Exception):
    """Unknown or unexpected status for first field."""


class Parser:
    """Validate field structure of an ECF results submission file.

    An event header must have one of each field in event_details, and is
    allowed more than one of each field in event_details_at_least_one.

    An event header must have exactly one of each field in one of the sets
    from each of environments and time_limits.  Note this means the
    ENVIRONMENT field is optional and it's value defaults to 'OTB'.

    The ECF ignores the fields in event_details_ignored, but these are
    accepted in submissions for historical reasons (in other words they
    were used at some time in the past).

    """

    def __init__(self, text, value_edge, no_value_tags):
        """Initialise the data structure."""
        self.fields = fields.FieldsFromText(text, value_edge, no_value_tags)
        self._expected_fields = None
        self._table = None
        self._switch = {
            constants.TABLE_VALUE: self._ignore_field,
            constants.ADJUDICATED: self._remove_field,
            constants.BCF_CODE: self._remove_ecf_code_and_aliases,
            constants.BCF_NO: self._remove_ecf_no_and_aliases,
            constants.BOARD: self._remove_field,
            constants.CLUB: self._remove_club_name_and_aliases,
            constants.CLUB_CODE: self._remove_field,
            constants.CLUB_COUNTY: self._remove_field,
            constants.CLUB_NAME: self._remove_club_name_and_aliases,
            constants.COLOUR: self._remove_field,
            constants.COLUMN: self._table_column,
            constants.COMMENT: self._remove_field,
            constants.COMMENT_LIST: self._remove_field,
            constants.COMMENT_PIN: self._remove_field,
            constants.DATE_OF_BIRTH: self._remove_field,
            constants.ECF_CODE: self._remove_ecf_code_and_aliases,
            constants.ECF_NO: self._remove_ecf_no_and_aliases,
            constants.ENVIRONMENT: self._remove_field,
            constants.EVENT_CODE: self._remove_field,
            constants.EVENT_DATE: self._remove_field,
            constants.EVENT_DETAILS: self._event_details,
            constants.EVENT_NAME: self._remove_field,
            constants.FIDE_NO: self._remove_field,
            constants.FINAL_RESULT_DATE: self._remove_field,
            constants.FINISH: self._finish,
            constants.FORENAME: self._remove_field,
            constants.GAME_DATE: self._remove_field,
            constants.GENDER: self._remove_field,
            constants.INFORM_FIDE: self._remove_field,
            constants.INFORM_CHESSMOVES: self._remove_field,
            constants.INFORM_GRAND_PRIX: self._remove_field,
            constants.INFORM_UNION: self._remove_field,
            constants.INITIALS: self._remove_field,
            constants.MATCH_RESULTS: self._match_results,
            constants.MINUTES_FIRST_SESSION: self._minutes_and_moves,
            constants.MINUTES_FOR_GAME: self._remove_minutes_for_game,
            constants.MINUTES_REST_OF_GAME: self._minutes_rest_of_game,
            constants.MINUTES_SECOND_SESSION: self._minutes_and_moves,
            constants.MOVES_FIRST_SESSION: self._minutes_and_moves,
            constants.MOVES_SECOND_SESSION: self._minutes_and_moves,
            constants.NAME: self._remove_field,
            constants.OTHER_RESULTS: self._other_results,
            constants.PIN: self._pin,
            constants.PIN1: self._remove_field,
            constants.PIN2: self._remove_field,
            constants.PLAYER_LIST: self._player_list,
            constants.RESULTS_DATE: self._remove_field,
            constants.RESULTS_DUPLICATED: self._remove_field,
            constants.RESULTS_OFFICER: self._remove_field,
            constants.RESULTS_OFFICER_ADDRESS: self._results_officer_address,
            constants.ROUND: self._remove_field,
            constants.SCORE: self._remove_field,
            constants.SECONDS_PER_MOVE: self._remove_field,
            constants.SECTION_RESULTS: self._section_results,
            constants.SUBMISSION_INDEX: self._remove_field,
            constants.SURNAME: self._remove_field,
            constants.TABLE_START: self._table_start,
            constants.TABLE_END: self._table_end,
            constants.TITLE: self._remove_field,
            constants.TREASURER: self._remove_field,
            constants.TREASURER_ADDRESS: self._treasurer_address,
            constants.WHITE_ON: self._remove_field,
        }
        self._switch_columns = {
            constants.TABLE_VALUE: self._ignore_field,
            constants.COLUMN: self._table_column,
            constants.TABLE_START: self._table_start,
        }
        self._switch_values = {
            constants.TABLE_VALUE: self._table_value,
            constants.TABLE_END: self._table_end,
        }

    @property
    def is_valid_result_submission_format(self):
        """Return True if self.text has a valid field structure."""
        return self.fields.error_tag is None

    @property
    def table_error(self):
        """Return True if table does not have a valid field structure."""
        return self.fields.error_tag == constants.TAG_ERROR_TABLE_LAYOUT

    def parse(self, widget, stop_at=constants.EVENT_DETAILS):
        """Split text into fields and validate field structure.

        widget is the tkinter.Text widget where the output is sent.

        stop_at is the field name at which parsibng will stop.  By default
        only the first field is expected to be parsed because it should be
        the EVENT DETAILS field.

        """
        # The function fields.insert_and_tag_name_value_into_document() is
        # used to append text and tags to widget, inserting newline before
        # selected field names.  There are no trailing newlines to handle
        # like in the builder.Builder.parse() method.
        self._expected_fields = expectedfields.ExpectedFields((None, None))
        match = field_re.match(self.fields.text_getter())
        if match:
            self._process_matches_after_first_field(
                widget,
                self._process_first_field_match(
                    widget, self._process_leading_text(widget, match), stop_at
                ),
                stop_at,
            )
        return self.fields

    def _process_leading_text(self, widget, match):
        """Return start of match if '#' starts match, or end of match.

        If the match does not start '#', the match is inserted into text
        as found.

        """
        if match.group().startswith(constants.FIELD_SEPARATOR):
            return match.start()
        try:
            status = self._unknown_name(widget, match.group(), None)
        except FieldTooLongError as exc:
            self.fields.fields_message = str(exc)
            return match.end()
        widget.insert(
            tkinter.INSERT, match.group(), (constants.FIELD_NAME_TAG, status)
        )
        return match.end()

    def _process_first_field_match(self, widget, start, stop_at):
        """Return end of match after adding field at start to document.

        The newline inserted after the previous field is not needed for
        the first field, unless there is some leading text before the
        first field.

        """
        match = field_re.match(self.fields.text_getter(), start)
        if not match:
            return start
        name, value, tag = self._split_match(match, widget)
        if tag == stop_at and tag in constants.PARSE_STOP_AT_FIELDS:
            return start
        try:
            status = self._switch.get(tag, self._unknown_name)(
                widget, tag, value
            )
        except FieldTooLongError as exc:
            self.fields.fields_message = str(exc)
            return match.end()
        if status == constants.STATUS_OK:
            self.fields.insert_name_value_without_newline_prefix(
                widget, tag, value, status
            )
        elif status == constants.STATUS_IGNORE:
            pass
        elif status == constants.TAG_ERROR_UNEXPECTED:
            self._add_non_ecf_format_first_field(
                widget,
                tag,
                value,
                status,
            )
        elif status == constants.TAG_ERROR_UNKNOWN:
            self._add_non_ecf_format_first_field(
                widget,
                name,
                value,
                status,
            )
        else:
            raise FirstFieldStatusError(
                status.join(("Field status '", "' not known or expected"))
            )
        return match.end()

    def _process_matches_after_first_field(self, widget, start, stop_at):
        """Add all fields after start to document."""
        status_ok = constants.STATUS_OK
        switch = self._switch
        unknown = self._unknown_name
        for match in field_re.finditer(self.fields.text_getter(), start):
            name, value, tag = self._split_match(match, widget)
            if tag == stop_at and tag in constants.PARSE_STOP_AT_FIELDS:
                break
            try:
                status = switch.get(tag, unknown)(widget, tag, value)
            except FieldTooLongError as exc:
                self.fields.fields_message = str(exc)
                return
            if status == status_ok:
                self.fields.insert_name_value(widget, tag, value, status)
            elif status == constants.STATUS_IGNORE:
                pass
            elif status == constants.STATUS_COLUMN:
                switch = self._switch_columns
                unknown = self._add_table_layout
            elif status == constants.STATUS_TABLE_START:
                switch = self._switch_values
                unknown = self._table_value
            elif status == constants.STATUS_TABLE_VALUE:
                self._table.add_value("".join(match.groups(default="")))
                switch = self._switch_values
                unknown = self._table_value
            elif status == constants.STATUS_TABLE_END:
                # This path is reachable only via _switch_values.
                # self._table._broken_column_definition will be False here.
                self._table = None
                switch = self._switch
                unknown = self._unknown_name
            elif status == constants.TAG_ERROR_UNEXPECTED:
                # None for _switch but Table instance for _switch_columns
                # and this path not reachable for _switch_values.
                self._add_non_ecf_format_field(
                    widget,
                    tag,
                    value,
                    status,
                )
            elif status == constants.TAG_ERROR_UNKNOWN:
                # None for _switch but Table instance for _switch_columns
                # and this path not reachable for _switch_values.
                self._add_non_ecf_format_field(
                    widget,
                    name,
                    value,
                    status,
                )
            else:
                raise FieldStatusError(
                    status.join(("Field status '", "' not known"))
                )
        return

    def _split_match(self, match, widget):
        """Return tuple of name, value, and tag, given match and widget.

        widget is needed to resolve the 'COMMENT' match, which occurs in
        two contexts: PLAYER LIST before any PIN fieldsets, and PIN within
        PLAYER LIST.  Tag COMMENT_LIST is generated for PLAYER LIST, and
        COMMENT_PIN for PIN, and COMMENT outside these two contexts.

        """
        item = "".join(match.groups(default="")).split(
            _NAME_VALUE_SEPARATOR, 1
        )
        if len(item) == 1:

            # If 'TABLE END' is actually a value in the table the
            # '#<name>=<value>#' format must be used instead.
            if (
                self._expected_fields.between_table_start_and_table_end
                and "".join(item[0].split()).upper() != constants.TABLE_END
            ):
                name = constants.TABLE_VALUE
                value = item[0].strip()
            else:
                name = item[0].strip()
                value = None

        else:
            name, value = (k.strip() for k in item)

        # Convert field names to tag names.
        # Single word field names are their own tag names.
        # The ECF specification states all characters except '\r' and
        # '\n' are significant in fields.
        # The ECF specification states spaces are ignored in field names.
        # The ECF implementation of importing results submission files
        # ignores case in field names and does not accept '\n' or '\r'
        # in field names.
        tag = "".join((name.split())).upper()
        tag = no_whitespace_name_to_short_tag_name.get(
            tag, self._pick_comment_tag(tag, widget)
        )

        return (name, value, tag)

    @staticmethod
    def _pick_comment_tag(tag, widget):
        """Return tag or the appropiate comment tag if tag is COMMENT."""
        if tag != constants.COMMENT:
            return tag
        index1 = tkinter.END
        nametag = constants.FIELD_NAME_TAG
        allparts = fields.SUFFIX_INCREMENT_NAMES
        playerlistparts = allparts.difference(
            set((constants.PLAYER_LIST, constants.PIN))
        )
        while True:
            prevrange = widget.tag_prevrange(nametag, index1)
            if not prevrange:
                return tag
            tags = set(widget.tag_names(prevrange[0])).intersection(allparts)
            if not tags:
                index1 = prevrange[0]
                continue
            tags.intersection_update(playerlistparts)
            if not tags or len(tags) != 1:
                return tag
            if constants.PIN in tags:
                return constants.COMMENT_PIN
            if constants.PLAYER_LIST in tags:
                return constants.COMMENT_LIST
            return tag

    def _add_table_layout(self, widget, tag, value):
        """Return 'unknown' or 'unexpected' status and force table layout.

        This method is used in the self._switch_columns which does not
        mention most field names and treats them as TAG_ERROR_UNKNOWN rather
        than TAG_ERROR_UNEXPECTED.  Make that distinction in this method.

        If a column definition sequence is interrupted by non-column data
        the anticipated table cannot be assumed correct when value count
        is an integer multiple of column definitions in the correct place
        relative to table start.

        """
        del widget, value
        self._table.set_column_definition_is_broken()
        if tag in constants.TAG_NAMES:
            return constants.TAG_ERROR_UNEXPECTED
        return constants.TAG_ERROR_UNKNOWN

    def _add_non_ecf_format_first_field(self, widget, name, value, status):
        """Add field or initial text which is not ECF submission format.

        Perhaps the wrong file was picked; or there is a typo in one or more
        submission format field names.

        """
        self.fields.insert_name_value_without_newline_prefix(
            widget, name, value, status
        )
        # Need a way of preserving repeating field counts for when this
        # method gets used in EVENT DETAILS part after address fields have
        # been gathered.
        self._expected_fields = self._expected_fields.__class__(
            self._expected_fields.context
        )

    def _add_non_ecf_format_field(self, widget, name, value, status):
        """Add field or initial text which is not ECF submission format.

        Perhaps the wrong file was picked; or there is a typo in one or more
        submission format field names.

        """
        if self._table is not None:
            # self._table._broken_column_definition must be True here.
            self.fields.append_table(widget, self._table)
            self._table.column_names.clear()
        if name not in constants.TAGS_START_NEWLINE:
            widget.insert(tkinter.INSERT, "\n")
        self.fields.insert_name_value(widget, name, value, status)
        # Need a way of preserving repeating field counts for when this
        # method gets used in EVENT DETAILS part after address fields have
        # been gathered.
        self._expected_fields = self._expected_fields.__class__(
            self._expected_fields.context
        )

    def _results_officer_address(self, widget, name, value):
        """Allow more than one RESULTS OFFICER ADDRESS field."""
        del widget, value
        if not self._expected_fields.remove_expected_field(name):
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields.add(name)
        return constants.STATUS_OK

    def _treasurer_address(self, widget, name, value):
        """Allow more than one TREASURER ADDRESS field."""
        del widget, value
        if not self._expected_fields.remove_expected_field(name):
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields.add(name)
        return constants.STATUS_OK

    def _remove_club_name_and_aliases(self, widget, name, value):
        """Remove ECF CODE and BCF CODE from set of expected field names."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        if name == constants.CLUB_NAME:
            self._expected_fields.discard(constants.CLUB)
            return constants.STATUS_OK
        self._expected_fields.discard(constants.CLUB_NAME)
        return constants.STATUS_OK

    def _remove_ecf_code_and_aliases(self, widget, name, value):
        """Remove ECF CODE and BCF CODE from set of expected field names."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        if name == constants.ECF_CODE:
            self._expected_fields.discard(constants.BCF_CODE)
            return constants.STATUS_OK
        self._expected_fields.discard(constants.ECF_CODE)
        return constants.STATUS_OK

    def _remove_ecf_no_and_aliases(self, widget, name, value):
        """Remove ECF CODE and BCF CODE from set of expected field names."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        if name == constants.ECF_NO:
            self._expected_fields.discard(constants.BCF_NO)
            return constants.STATUS_OK
        self._expected_fields.discard(constants.ECF_NO)
        return constants.STATUS_OK

    def _remove_field(self, widget, name, value):
        """Return result of removing name from set of expected field names."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        return constants.STATUS_OK

    def _remove_minutes_for_game(self, widget, name, value):
        """Remove MINUTES FOR GAME from set of expected field names.

        The options ruled out by this option are removed, and will cause
        an exception if found later.

        """
        del widget, value
        if not self._expected_fields.remove_minutes_for_game(name):
            return constants.TAG_ERROR_UNEXPECTED
        return constants.STATUS_OK

    def _minutes_and_moves(self, widget, name, value):
        """Remove name and MINUTES FOR GAME from expected field name set.

        There are two pairs of fields which must have both or neither
        members present; which cannot be handled till end of part.

        """
        del widget, value
        if not self._expected_fields.remove_minutes_and_moves(name):
            return constants.TAG_ERROR_UNEXPECTED
        return constants.STATUS_OK

    def _minutes_rest_of_game(self, widget, name, value):
        """Remove name and MINUTES FOR GAME from expected field name set.

        There are two pairs of fields which must have both or neither
        members present; which cannot be handled till end of part.

        """
        del widget, value
        if not self._expected_fields.remove_minutes_rest_of_game(name):
            return constants.TAG_ERROR_UNEXPECTED
        return constants.STATUS_OK

    def _event_details(self, widget, name, value):
        """Set expected field names for EVENT DETAILS part of submission."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields = expectedfields.EventDetails((name, None))
        return constants.STATUS_OK

    def _validate_event_details_field_combinations(self):
        """Validate EVENT DETAILS part when PLAYER LIST or FINISH found."""
        if self._expected_fields.validate_event_details_field_combinations():
            return constants.STATUS_OK
        return constants.TAG_ERROR_UNEXPECTED

    def _player_list(self, widget, name, value):
        """Set expected field names at start of PLAYER LIST submission part."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._validate_event_details_field_combinations()
        self._expected_fields = expectedfields.ExpectedFields((name, None))
        return constants.STATUS_OK

    def _pin(self, widget, name, value):
        """Validate and set expected field names for PIN group."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields.validate_pin_field_combinations()
        self._expected_fields = expectedfields.ExpectedFields(
            (name, constants.PLAYER_LIST)
        )
        return constants.STATUS_OK

    def _validate_pin1_field(self):
        """Check mandatory fields after PIN1 terminating field found.

        One validation method is ok for all *_pin1_* methods because only
        existence of mandatory fields needs checking.

        """
        if self._expected_fields.intersection(constants.MANDATORY_PIN1_FIELDS):
            return constants.TAG_ERROR_UNEXPECTED
        return constants.STATUS_OK

    def _match_results(self, widget, name, value):
        """Set expected field names for start of MATCH RESULTS part.

        A PIN1 field should still be expected and must be removed too
        before validating the PIN1 group.

        """
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields.validate_pin_field_combinations()
        self._validate_pin1_field()
        self._expected_fields = expectedfields.ExpectedFields((name, None))
        self._switch[constants.PIN1] = self._pin1_in_match
        return constants.STATUS_OK

    def _pin1_in_match(self, widget, name, value):
        """Validate and set expected fields for PIN group in MATCH RESULTS."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._validate_pin1_field()
        self._expected_fields = expectedfields.ExpectedFields(
            (name, constants.MATCH_RESULTS)
        )
        return constants.STATUS_OK

    def _other_results(self, widget, name, value):
        """Set expected field names for start of OTHER RESULTS part.

        A PIN1 field should still be expected and must be removed too
        before validating the PIN1 group.

        """
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields.validate_pin_field_combinations()
        self._validate_pin1_field()
        self._expected_fields = expectedfields.ExpectedFields((name, None))
        self._switch[constants.PIN1] = self._pin1_in_other
        return constants.STATUS_OK

    def _pin1_in_other(self, widget, name, value):
        """Validate and set expected fields for PIN group in OTHER RESULTS."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._validate_pin1_field()
        self._expected_fields = expectedfields.ExpectedFields(
            (name, constants.OTHER_RESULTS)
        )
        return constants.STATUS_OK

    def _section_results(self, widget, name, value):
        """Set expected field names for start of SECTION RESULTS part.

        A PIN1 field should still be expected and must be removed too
        before validating the PIN1 group.

        """
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields.validate_pin_field_combinations()
        self._validate_pin1_field()
        self._expected_fields = expectedfields.ExpectedFields((name, None))
        self._switch[constants.PIN1] = self._pin1_in_section
        return constants.STATUS_OK

    def _pin1_in_section(self, widget, name, value):
        """Verify and set expected fields for PIN group in SECTION RESULTS."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._validate_pin1_field()
        self._expected_fields = expectedfields.ExpectedFields(
            (name, constants.SECTION_RESULTS)
        )
        return constants.STATUS_OK

    def _finish(self, widget, name, value):
        """Validate final group before FINISH and set nothing expected."""
        del widget, value
        if constants.PLAYER_LIST in self._expected_fields:
            self._validate_event_details_field_combinations()
        self._expected_fields.validate_pin_field_combinations()
        self._validate_pin1_field()
        self._expected_fields = expectedfields.ExpectedFields((name, None))
        return constants.STATUS_OK

    def _table_column(self, widget, name, value):
        """Validate table column name."""
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields.validate_pin_field_combinations()

        # Pretend the field is PIN1 for _validate_pin1() call, then put
        # PIN1 field back for the validation which happens if the table
        # has not yet been created.
        self._validate_pin1_field()

        fields_replaced_by_column = constants.SUBPART_TAGS
        if self._table is None:
            if not self._expected_fields.intersection(
                fields_replaced_by_column
            ):
                return constants.TAG_ERROR_UNEXPECTED
            if len(
                self._expected_fields.intersection(fields_replaced_by_column)
            ) == len(fields_replaced_by_column):
                return constants.TAG_ERROR_UNEXPECTED
            for replaced_field in fields_replaced_by_column:
                if replaced_field in self._expected_fields:
                    table_type = self._get_table_type(widget)
                    if table_type is None:
                        return constants.TAG_ERROR_UNEXPECTED
                    self._table = table.Table(replaced_field, table_type)
                    break
        value = value.upper()
        if not self._table.add_column_name(
            column_name_to_short_tag_name.get(value, value)
        ):
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields = expectedfields.ExpectedFields((name, None))
        return constants.STATUS_COLUMN

    @staticmethod
    def _table_value(*args):
        """Collect table value field ('#<any text>#')."""
        # Need match object rather than the derived name and value.
        # Delay processing till switch on return value, to avoid changing
        # the (widget, name, value) arguments everywhere.
        del args
        return constants.STATUS_TABLE_VALUE

    def _table_start(self, widget, name, value):
        """Switch column name and table value collection on."""
        del widget, value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields = expectedfields.TableStart((name, None))
        return constants.STATUS_TABLE_START

    def _table_end(self, widget, name, value):
        """Get <name=value>s from table and set table value collection off."""
        del value
        if self._expected_fields.remove_expected_field(name) is False:
            return constants.TAG_ERROR_UNEXPECTED
        self._expected_fields = expectedfields.ExpectedFields(
            self._table.get_key_for_context_at_end_table()
        )
        self.fields.append_table(widget, self._table)
        self._expected_fields = self._expected_fields.__class__(
            self._expected_fields.context
        )
        return constants.STATUS_TABLE_END

    @staticmethod
    def _get_table_type(widget):
        """Return identifier for location of table.

        Look back through fields for most recent of PLAYER LIST,
        MATCH RESULTS, OTHER RESULTS, and SECTION RESULTS, and use
        whichever is found.

        """
        table_types = constants.TABLE_TYPES
        index1 = tkinter.END
        nametag = constants.FIELD_NAME_TAG
        while True:
            prevrange = widget.tag_prevrange(nametag, index1)
            if not prevrange:
                return None
            fieldname = widget.get(*prevrange).upper()
            fieldname = record_type_name_to_short_tag_name.get(
                fieldname, fieldname
            )
            if fieldname not in table_types:
                index1 = prevrange[0]
                continue
            return fieldname

    @staticmethod
    def _ignore_field(widget, name, value):
        """Explicitly ignore empty ('##') fields for table compatibility."""
        del widget, name, value
        return constants.STATUS_IGNORE

    @staticmethod
    def _unknown_name(widget, name, value):
        """Return TAG_ERROR_UNKNOWN if name and value short and name unknown.

        Raise FieldTooLongError for names or values which are too long.

        """
        del widget
        if value is not None and len(value) > 100:
            raise FieldTooLongError(
                str(len(value)).join(
                    (
                        "Value length '",
                        "' too long: is file an ECF results submission file?",
                    )
                )
            )
        if len(name) > 40:
            if len(name) > 20:
                name = name[:20] + "..."
            raise FieldTooLongError(
                name.join(
                    (
                        "Field name '",
                        "' too long (",
                        str(len(name)),
                        "): is file an ECF results submission file?",
                    )
                )
            )
        return constants.TAG_ERROR_UNKNOWN
