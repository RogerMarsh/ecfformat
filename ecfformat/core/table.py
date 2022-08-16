# table.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Convert ECF result file table structure to PIN and PIN1 field sequences.

The table structure defines the interpretation of a sequence of '#'
delimited values.  The PIN and PIN1 field sequences present the data as
a sequence of '#' delimited <field=value> items.

"""

from . import constants

fields_allowed_in_table = {
    constants.OTHER_RESULTS: frozenset(constants.FIELDS_ALLOWED_IN_OTHER),
    constants.MATCH_RESULTS: frozenset(constants.FIELDS_ALLOWED_IN_MATCH),
    constants.SECTION_RESULTS: frozenset(constants.FIELDS_ALLOWED_IN_SECTION),
    constants.PLAYER_LIST: frozenset(constants.FIELDS_ALLOWED_IN_PLAYERS),
}
field_set_terminators = {
    constants.PIN: constants.PIN_SET_TERMINATORS,
    constants.PIN1: constants.PIN1_SET_TERMINATORS,
}
field_name_as_value_to_name = {
    (constants.PIN1, constants.COMMENT): constants.COMMENT_PIN,
    (constants.PIN, constants.COMMENT): constants.COMMENT_LIST,
}


class ReplaceFieldsetError(Exception):
    """Exception indicates attempt to use a fieldset which cannot be in table.

    Fields PIN and PIN1 are the valid fields which start a fieldset.

    """


class ReplacePartError(Exception):
    """Exception indicates attempt to use a part which cannot be in table.

    Fields PLAYER LIST, OTHER RESULTS, MATCH RESULTS, and SECTION RESULTS,
    are the valid fields which start a part.

    """


class ColumnDefinitionBrokenError(Exception):
    """Exception indicates attempt set a broken table as not broken."""


class Table:
    """The data structure of a table in an ECF results submission file.

    The PIN set of fields in the Player List and the PIN1 set of fields in
    the Match, Other, and Section, results parts can be replaced by a
    table structure defined by COLUMN, TABLE START,and TABLE END fields.

    The intention seems to be to allow tables to be used instead of PIN,
    PIN1, and associated fields.  Howver this class allows any sequence of
    PIN and PIN1 sets of fields to be replaced: PIN, PIN1, and TABLE, can
    be mixed in the input.

    The Table class allows replacement of a table structure by an equivalent
    PIN or PIN1 structure.

    """

    def __init__(self, replaced_name, variant_name):
        """Initialise table.

        replaced_name will be PIN or PIN1.
        variant_name will be PLAYER LIST, OTHER RESULTS, MATCH RESULTS,
        or SECTION RESULTS.

        """
        if replaced_name not in constants.SUBPART_TAGS:
            raise ReplaceFieldsetError(
                replaced_name.join(
                    (
                        "Cannot replace field ",
                        " by table",
                    )
                )
            )
        if variant_name not in constants.TABLE_TYPES:
            raise ReplacePartError(
                variant_name.join(
                    (
                        "Table replacement for ",
                        " is not allowed",
                    )
                )
            )
        self._replaced_name = replaced_name
        self._table_type = variant_name
        self._allowed_fields = set(fields_allowed_in_table[self._table_type])
        self.column_names = []
        self.values = []
        self._broken_column_definition = False

    @property
    def broken_column_definition(self):
        """Return column definition status."""
        return self._broken_column_definition

    def set_column_definition_is_broken(self):
        """Set column definition status to broken.

        self._broken_column_definition is initialized False.

        This method allows self._broken_column_definition to be set True
        if something goes wrong defining columns before the TABLE START
        field indicates start of table for the defined columns, including
        not defining any columns at all.

        """
        self._broken_column_definition = True

    def _remove_allowed_field(self, name):
        """Remove name from set of allowed fields.

        The implication of a KeyError exception is an attempt to define a
        column for a field not accepted in the place where a table is being
        defined.

        """
        try:
            self._allowed_fields.remove(name)
        except KeyError:
            return False
        return True

    def add_column_name(self, name):
        """Append name to list of column names if allowed in table.

        The existence of a column for a field name does not imply it will
        be valid to assign a non-null value in all 'rows'.  Some columns
        may be used only if others are, for example.

        """
        if self._remove_allowed_field(name):
            self.column_names.append(name)
            return True
        return False

    def add_value(self, value):
        """Append value to list of values in table.

        The existence of a column for a field name does not imply it will
        be valid to assign a non-null value in all 'rows'.  Some columns
        may be used only if others are, for example.

        """
        self.values.append(value.strip("\n"))

    def get_key_for_context_at_end_table(self):
        """Return key into dict of ExpectedFields arguments for new context.

        These are the expected column names before any columns are defined
        plus the field names which imply termination of the PIN or PIN1
        set defined by expected column names.

        """
        return (self._replaced_name, self._table_type)

    def get_table_fields(self):
        """Return collected table fields.

        The COLUMN fields are placed one per line.

        The TABLE START and TABLE END fields are placed on their own line.

        The table values, between TABLE START and TABLE END, are placed
        with n per line where n is the number of COLUMN fields.

        """
        column_names = self.column_names
        field_separator = constants.FIELD_SEPARATOR
        fields = []
        for name in column_names:
            fields.append([constants.COLUMN, name])
        if self.values:
            fields.append([constants.TABLE_START, None])
            fieldset = []
            for value in self.values:
                fieldset.append(value)
                if len(fieldset) < len(column_names):
                    continue
                fields.append([None, field_separator.join(fieldset)])
                fieldset.clear()
            if fieldset:
                fields.append([None, field_separator.join(fieldset)])
                fieldset.clear()
            fields.append([constants.TABLE_END, None])
        return fields

    def translate_table_to_name_value_pairs(self):
        r"""Return <name=value> list for table or original invalid table.

        If the number of table values is not an integer multiple of the
        number of columns a single value is returned including the '#'
        delimiters.  The single value is surrounded by the COLUMN,
        TABLE START, and TABLE END, fields used to define the table.
        Otherwise just the <name=value> items are returned.  This is
        sufficient to decide if the original table structure was valid.

        The table layout is not significant: in particular '\n' has no
        impact on the validity of the table.  Well placed newlines merely
        make the table easier to eyeball when looking at *.txt files.

        This translation cannot imply the validity of the content: are
        the values consistent and so forth.

        """
        if self._broken_column_definition or len(self.values) % len(
            self.column_names
        ):
            return self.get_table_fields()
        column_names = self.column_names
        replaced_name = self._replaced_name
        fieldset = {}
        column_names.insert(
            0, column_names.pop(column_names.index(replaced_name))
        )
        fields = []
        for serial, value in enumerate(self.values):
            fieldset[column_names[serial % len(column_names)]] = value
            if len(fieldset) < len(column_names):
                continue
            fields.append([replaced_name, fieldset[replaced_name]])
            for name in column_names[1:]:
                fields.append(
                    [
                        field_name_as_value_to_name.get(
                            (replaced_name, name), name
                        ),
                        fieldset[name],
                    ]
                )
            fieldset = {}
        return fields
