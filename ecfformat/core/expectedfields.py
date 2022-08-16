# expectedfields.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Track the expected fields at the insertion point.

The parser uses this to decide if the next field is permitted at the end
of the text collected so far.

The inserter initializes expected fields with those already present in the
context of the insertion point, and allows insertion by edit of any field
still expected.

"""

from . import constants

expected_fields = {
    (constants.EVENT_DETAILS, None,): (
        frozenset(
            (
                constants.PLAYER_LIST,
                constants.FINISH,
            )
        )
        .union(constants.MANDATORY_EVENT_FIELDS)
        .union(constants.OPTIONAL_EVENT_FIELDS)
    ),
    (constants.MATCH_RESULTS, None,): frozenset(
        (
            constants.PIN1,
            constants.WHITE_ON,
            constants.RESULTS_DATE,
        )
        + constants.PIN1_SET_TERMINATORS
    ),
    (constants.PIN1, constants.MATCH_RESULTS,): frozenset(
        constants.FIELDS_ALLOWED_IN_MATCH + constants.PIN1_SET_TERMINATORS
    ),
    (constants.PIN1, constants.OTHER_RESULTS,): frozenset(
        constants.FIELDS_ALLOWED_IN_OTHER + constants.PIN1_SET_TERMINATORS
    ),
    (constants.PIN1, constants.SECTION_RESULTS,): frozenset(
        constants.FIELDS_ALLOWED_IN_SECTION + constants.PIN1_SET_TERMINATORS
    ),
    (
        constants.FINISH,
        None,
    ): frozenset(),
    (constants.COLUMN, constants.PLAYER_LIST,): frozenset(
        (
            constants.COLUMN,
            constants.TABLE_START,
        )
    ),
    (constants.TABLE_START, None,): frozenset(
        (
            constants.TABLE_VALUE,
            constants.TABLE_END,
        )
    ),
    (constants.PLAYER_LIST, None,): frozenset(
        (
            constants.COMMENT,
            constants.PIN,
        )
        + constants.PIN1_SET_TERMINATORS
    ),
    # '(constants.PIN, None,)' would be the key, except for the interaction
    # with the Table class.  Element [1] of the key was introduced to cope
    # with the different fields allowed in the PIN1 set depending on the
    # parent part, MATCH RESULTS for example.
    (constants.PIN, constants.PLAYER_LIST,): frozenset(
        constants.FIELDS_ALLOWED_IN_PLAYERS
        + constants.PLAYERS_SET_TERMINATORS
        + (constants.COLUMN,)
    ),
    (
        True,
        None,
    ): True,
    (
        None,
        None,
    ): frozenset((constants.EVENT_DETAILS,)),
}
# black and pycodestyle disagree about 'name[ind1, ind2,]' so drop the ','
# just before the ']'.  There are several cases here.
expected_fields[constants.OTHER_RESULTS, None] = expected_fields[
    constants.MATCH_RESULTS,
    None,
]
expected_fields[constants.SECTION_RESULTS, None] = expected_fields[
    constants.MATCH_RESULTS,
    None,
]
expected_fields[constants.COLUMN, None] = expected_fields[
    constants.COLUMN,
    constants.PLAYER_LIST,
]
expected_fields[constants.COLUMN, constants.MATCH_RESULTS] = expected_fields[
    constants.COLUMN,
    constants.PLAYER_LIST,
]
expected_fields[constants.COLUMN, constants.OTHER_RESULTS] = expected_fields[
    constants.COLUMN,
    constants.PLAYER_LIST,
]
expected_fields[
    constants.COLUMN,
    constants.SECTION_RESULTS,
] = expected_fields[
    constants.COLUMN,
    constants.PLAYER_LIST,
]
expected_fields[
    constants.TABLE_END,
    constants.MATCH_RESULTS,
] = expected_fields[
    constants.PIN1,
    constants.MATCH_RESULTS,
]
expected_fields[
    constants.TABLE_END,
    constants.OTHER_RESULTS,
] = expected_fields[
    constants.PIN1,
    constants.OTHER_RESULTS,
]
expected_fields[
    constants.TABLE_END,
    constants.SECTION_RESULTS,
] = expected_fields[
    constants.PIN1,
    constants.SECTION_RESULTS,
]
expected_fields[constants.TABLE_END, constants.PLAYER_LIST] = expected_fields[
    constants.PLAYER_LIST,
    None,
]

# Most fields which do not have a field structure defined are mandatory,
# exactly one occurrence, or optional, either zero or one occurrence, in a
# set of fields.  The *_RESULTS, PIN, PIN1, COLUMN, TABLE START, and
# TABLE END, fields define field structures and are not defined as
# repeatable, even though they can repeat in a set of fields.
# RESULTS OFFICER ADDRESS and TREASURER ADDRESS are mandatory and repeatable,
# and occur in the EVENT DETAILS set.
repeatable_fields = {key: frozenset() for key in expected_fields}
repeatable_fields[constants.EVENT_DETAILS, None] = frozenset(
    (
        constants.RESULTS_OFFICER_ADDRESS,
        constants.TREASURER_ADDRESS,
    )
)


class ExpectedFields:
    """Create set of expected fields for context and remove found fields."""

    between_table_start_and_table_end = False

    def __init__(self, context, found=None):
        """Set expected_fields for context and remove fields in found."""
        if found is None:
            found = set()
        self._expected_fields = set(expected_fields[context].difference(found))
        self._repeatable_fields = repeatable_fields[context]
        self._context = context

    def __contains__(self, name):
        """Return True if name is in the expected fields set."""
        return name in self._expected_fields

    def intersection(self, name_set):
        """Return intersection of self._expected_fields and name_set."""
        return self._expected_fields.intersection(name_set)

    def add(self, name):
        """Add name to expected fields."""
        self._expected_fields.add(name)

    def discard(self, name):
        """Discard name from expected fields."""
        self._expected_fields.discard(name)

    def remove_expected_field(self, name):
        """Return True if name is expected, and False if not expected.

        False implies a format error in the ECF results submission file.

        """
        try:
            self._expected_fields.remove(name)
        except KeyError:
            return False
        return True

    def remove_minutes_for_game(self, name):
        """Remove MINUTES FOR GAME from set of expected field names.

        The options ruled out by this option are removed, and will cause
        an exception if found later.

        """
        if not self.remove_expected_field(name):
            return False
        self._expected_fields.discard(constants.MINUTES_FIRST_SESSION)
        self._expected_fields.discard(constants.MOVES_FIRST_SESSION)
        self._expected_fields.discard(constants.MINUTES_SECOND_SESSION)
        self._expected_fields.discard(constants.MOVES_SECOND_SESSION)
        self._expected_fields.discard(constants.MINUTES_REST_OF_GAME)
        return True

    def remove_minutes_and_moves(self, name):
        """Remove name and MINUTES FOR GAME from expected field name set.

        There are two pairs of fields which must have both or neither
        members present; which cannot be handled till end of part.

        """
        if not self.remove_expected_field(name):
            return False
        self._expected_fields.discard(constants.MINUTES_FOR_GAME)
        return True

    def remove_minutes_rest_of_game(self, name):
        """Remove name and MINUTES FOR GAME from expected field name set.

        There are two pairs of fields which must have both or neither
        members present; which cannot be handled till end of part.

        """
        if not self.remove_expected_field(name):
            return False
        self._expected_fields.discard(constants.MINUTES_FOR_GAME)
        return True

    @staticmethod
    def validate_event_details_field_combinations():
        """Return True.

        The EventDetails class overrides this method to provide validation
        when the end of the EVENT DETAILS part is found.

        Usually the PLAYER LIST part follows EVENT DETAILS but FINISH is
        allowed to follow too.

        """
        return True

    @property
    def context(self):
        """Return self._context, assumed context after table or error."""
        return self._context

    def validate_pin_field_combinations(self):
        """Check conditional fields after PIN terminating field found.

        This is another PIN; or one of MATCH RESULTS, OTHER_RESULTS,
        SECTION RESULTS, and FINISH.

        """
        if (
            len(
                self._expected_fields.intersection(
                    constants.ALTERNATIVE_NAME_FIELDS
                )
            )
            != 1
        ):
            return constants.TAG_ERROR_UNEXPECTED
        if constants.NAME not in self._expected_fields:
            if len(
                self._expected_fields.intersection(
                    constants.FORENAME_INITIAL_FIELDS
                )
            ) != len(constants.FORENAME_INITIAL_FIELDS):
                return constants.TAG_ERROR_UNEXPECTED
        if constants.ECF_CODE in self._expected_fields:
            if constants.CLUB_CODE in self._expected_fields:
                return constants.TAG_ERROR_UNEXPECTED
        if constants.CLUB_CODE in self._expected_fields:
            if constants.CLUB_NAME not in self._expected_fields:
                return constants.TAG_ERROR_UNEXPECTED
            if constants.CLUB_COUNTY not in self._expected_fields:
                return constants.TAG_ERROR_UNEXPECTED
        return None


class EventDetails(ExpectedFields):
    """Custom ExpectedFields for EVENT DETAILS.

    The time limit fields have complicated inter-dependencies.

    The RESULTS OFFICER ADDRESS and TREASURER ADDRESS fields can be repeated.

    """

    def __init__(self, *args, **kwargs):
        """Delegate then add flags for the repeatable and time limit fields."""
        super().__init__(*args, **kwargs)
        self._time_limit_field_count = 0
        self._results_officer_address_count = 0
        self._treasurer_address_count = 0

    def add(self, name):
        """Delegate then increment name count if repeatable."""
        super().add(name)
        if name == constants.RESULTS_OFFICER_ADDRESS:
            self._results_officer_address_count += 1
        elif name == constants.TREASURER_ADDRESS:
            self._treasurer_address_count += 1

    def remove_minutes_for_game(self, name):
        """Delegate then increment time limit field count."""
        if not super().remove_minutes_for_game(name):
            return False
        self._time_limit_field_count += 2
        return True

    def remove_minutes_and_moves(self, name):
        """Delegate then increment time limit field count."""
        if not super().remove_minutes_and_moves(name):
            return False
        self._time_limit_field_count += 1
        return True

    def remove_minutes_rest_of_game(self, name):
        """Delegate then increment time limit field count."""
        if not super().remove_minutes_rest_of_game(name):
            return False
        self._time_limit_field_count += 2
        return True

    def validate_event_details_field_combinations(self):
        """Return True if time limit and repeatable fields are valid."""
        if self._treasurer_address_count:
            if (
                self.remove_expected_field(constants.TREASURER_ADDRESS)
                is False
            ):
                return False
        if self._results_officer_address_count:
            if (
                self.remove_expected_field(constants.RESULTS_OFFICER_ADDRESS)
                is False
            ):
                return False
        if self._expected_fields.intersection(
            constants.MANDATORY_EVENT_FIELDS
        ):
            return False
        if not self._time_limit_field_count or bool(
            self._time_limit_field_count % 2
        ):
            return False
        return True


class TableStart(ExpectedFields):
    """Custom ExpectedFields for TABLE START."""

    between_table_start_and_table_end = True
