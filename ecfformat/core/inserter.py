# inserter.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Build ECF results submission structure elements to be inserted in text."""

import tkinter

from .sequences import method_name_suffix
from . import constants
from .context import Context

sequence_insert_map = {}


def populate_sequence_insert_map(map_=None, sequence=None):
    """Build map_ from sequences.

    This method is provided to initialize sequence_insert_map in modules
    which implement subclasses of Inserter.

    map_ should be that module's equivalent of sequence_insert_map.
    sequence should be the appropriate *_SEQUENCES attribute in sequences
    module.

    """
    if map_ is None:
        map_ = {}
    if sequence is None:
        sequence = ()
    for item in sequence:
        key = "_".join(("_handle", method_name_suffix(item[4])))
        key = item[4][0]
        value = item[4][1]
        if key in map_:
            if map_[key] != value:
                raise InserterError(
                    "".join(
                        (
                            "Inconsistent field insertions defined for '",
                            key,
                            "'",
                        )
                    )
                )
            continue
        map_[key] = value


class InserterError(Exception):
    """Exception class for inserter module."""


class Inserter:
    """Build field structure for insertion into text at a chosen point.

    An inserter is created for the point at which insertion is chosen.

    The field structure is inserted after the current field, at the end of
    the current set of field, or at the end of the current part of the
    submission.

    """

    def __init__(self):
        """Initialise for insertion relative to set of tag_names at index."""
        self.verify_sequence_insert_map()
        self._widget = None
        self._content = None

        # There needs to be at least one statement in this class binding
        # self.context to a sequence so pylint E0633 messages about
        # 'unpacking-non-sequence' are avoided.
        # Neatest solution seems to be make context a property and test
        # for valid values in the setter.
        self._context = None

    @property
    def context(self):
        """Return context."""
        return self._context

    @context.setter
    def context(self, value):
        if value is None:
            self._context = value
        elif isinstance(value, tuple) and len(value) == 6:
            self._context = Context(*value)
        else:
            raise InserterError("value must be 'None' or tuple of length 6")

    def verify_sequence_insert_map(self, map_from_subclass=None):
        """Verify map_from_subclass is consistent with sequence_insert_map.

        sequence_insert_map is an attribute of inserter module.

        """
        self._verify_sequence_insert_map(
            map_=sequence_insert_map, map_from_subclass=map_from_subclass
        )

    @staticmethod
    def _verify_sequence_insert_map(map_, map_from_subclass=None):
        """Raise exception if map_from_subclass contradicts map_.

        map_from_subclass is an empty dict by default.

        """
        if map_from_subclass is None:
            map_from_subclass = {}
        for key in set(map_).intersection(map_from_subclass):
            if map_[key] != map_from_subclass[key]:
                raise InserterError(
                    "".join(
                        (
                            "Inconsistent field insertions defined for '",
                            key,
                            "' in subclass' module",
                        )
                    )
                )
        map_from_subclass.update(map_)
        return map_from_subclass

    def get_sequence_insert_map_item(self, key):
        """Return field list for key, delegate if key is not found."""
        for map_ in self._get_sequence_insert_map():
            value = map_.get(key)
            if value is None:
                continue
            return value
        raise InserterError("No field list found for " + key)

    @staticmethod
    def _get_sequence_insert_map():
        """Return list containing sequence_insert_map or empty list."""
        if sequence_insert_map:
            return [sequence_insert_map]
        return []

    def _insert_field(self, name):
        """Insert field called name if not already present in field set.

        Field sets are identified by fields PIN and PIN1, and by the
        EVENT DETAILS, PLAYER LIST, MATCH RESULTS, OTHER RESULTS, and
        SECTION RESULTS, parts for fields not in the PIN and PIN1 sets.

        A few fields can occur more than once in their sets: these must
        be handled separately (TREASURER ADDRESS for example).

        """
        self._content.insert_name_value(
            self._widget,
            name,
            "" if name not in constants.NAME_ONLY_FIELDS else None,
            None,
        )

    def insert_fields(self, sequencekey, widget, content):
        """Insert each field for sequencekey into widget and content.

        The insertion order is implied by 'for field in sequencekey'.

        widget is the tkinter Text instance displaying content.
        content is the Fields (or a subclass) instance containing document.

        """
        if self.context is None:
            return
        self._widget = widget
        self._content = content
        type_field = self.get_sequence_insert_map_item(sequencekey)[0]
        if type_field in constants.RECORD_TAGS:
            self._insert_part_fields(sequencekey)
        elif type_field in constants.SUBPART_TAGS:
            if self.context.part == self.context.record:
                self._insert_record_fields_before_next(sequencekey, type_field)
            else:
                self._insert_record_fields_after_record(sequencekey)
        else:
            self._insert_fields_in_record(sequencekey)
        self._widget = None
        self._content = None
        return

    def _insert_part_fields(self, sequencekey):
        """Insert fields for a new part after current part.

        See insert_fields docstring for argument descriptions.

        """
        widget = self._widget
        restore_insert = widget.index(tkinter.INSERT)
        widget.mark_set(
            tkinter.INSERT, widget.tag_ranges(self.context.part_id)[-1]
        )
        for name in self.get_sequence_insert_map_item(sequencekey):
            self._insert_field(name)
        widget.mark_set(tkinter.INSERT, restore_insert)

    def _insert_record_fields_before_next(self, sequencekey, type_field):
        """Insert fields for new record before next record or part end.

        See insert_fields docstring for argument descriptions.

        Insert a new record of the expected type in the part immediately
        before the first record in the part, or at the end of the part if
        there are no records in the part.  The record is inserted after
        any fields in the part, which do not belong to records in the part,
        that appear before the first record.

        """
        widget = self._widget
        restore_insert = widget.index(tkinter.INSERT)
        insert_at = widget.tag_nextrange(type_field, tkinter.INSERT)
        record_end = widget.tag_prevrange(
            self.context.record_id,
            tkinter.END,
        )[-1]
        if not insert_at:
            widget.mark_set(tkinter.INSERT, record_end)
            for name in self.get_sequence_insert_map_item(sequencekey):
                self._insert_field(name)
        else:
            if widget.compare(record_end, ">", insert_at[0]):
                insert_at = widget.search(
                    constants.FIELD_SEPARATOR, insert_at[0], backwards=True
                )
            else:
                insert_at = widget.search(
                    constants.FIELD_SEPARATOR, record_end
                )
            widget.mark_set(tkinter.INSERT, insert_at)
            for name in self.get_sequence_insert_map_item(sequencekey):
                self._content.insert_name_value_without_newline_prefix(
                    self._widget, name, "", None
                )
        if widget.get(tkinter.INSERT) != "\n":
            widget.insert(tkinter.INSERT, "\n")
        widget.mark_set(tkinter.INSERT, restore_insert)

    def _insert_record_fields_after_record(self, sequencekey):
        """Insert fields for new record after current record.

        See insert_fields docstring for argument descriptions.

        Inserts a new record of same type as current record immediately
        after the current record.

        """
        widget = self._widget
        restore_insert = widget.index(tkinter.INSERT)
        widget.mark_set(
            tkinter.INSERT, widget.tag_ranges(self.context.record_id)[-1]
        )
        fields = self.get_sequence_insert_map_item(sequencekey)
        for name in fields:
            self._insert_field(name)
        widget.mark_set(tkinter.INSERT, restore_insert)

    def _insert_fields_in_record(self, sequencekey):
        """Insert fields for record in current record.

        See insert_fields docstring for argument descriptions.

        """
        # Newline handling is broken but seems to give the desired outcome.
        # 'if widget.get(widget.tag_ranges(record_id)[-1]) != "\n":'? and
        # 'insert_at = insert_at + "-1c"'?, possibly because if the block
        # ends with a newline the relevent fields end with a newline too.
        record = self.context.record
        record_id = self.context.record_id
        widget = self._widget
        restore_insert = widget.index(tkinter.INSERT)
        record_end = widget.tag_ranges(record_id)[-1]
        next_field = widget.tag_nextrange(
            constants.FIELD_NAME_TAG,
            tkinter.INSERT,
            record_end,
        )
        if next_field:
            if widget.compare(next_field[0], "==", tkinter.INSERT):
                next_field = widget.tag_nextrange(
                    constants.FIELD_NAME_TAG,
                    next_field[-1],
                    record_end,
                )
        if next_field:
            insert_at = widget.search(
                constants.FIELD_SEPARATOR, next_field[0], backwards=True
            )
            starts_on_newline = constants.TAGS_START_NEWLINE.intersection(
                widget.tag_names(next_field[0])
            )
            if starts_on_newline:
                insert_at = insert_at + "-1c"
        else:
            starts_on_newline = False
            insert_at = record_end
        widget.mark_set(tkinter.INSERT, insert_at)
        for name in self.get_sequence_insert_map_item(sequencekey):
            self._insert_field(name)
        if record in constants.PART_TAGS:
            if widget.get(widget.tag_ranges(record_id)[-1]) != "\n":
                if not starts_on_newline:
                    widget.insert(tkinter.INSERT, "\n")
        widget.mark_set(tkinter.INSERT, restore_insert)

    @staticmethod
    def insert_finish(widget, content):
        """Insert FINISH before next EVENT DETAILS, or after last field."""
        last_name_range = widget.tag_prevrange(
            constants.FIELD_NAME_TAG, tkinter.END
        )
        next_event_range = widget.tag_nextrange(
            constants.EVENT_DETAILS, tkinter.INSERT
        )
        if next_event_range:
            index = next_event_range[0]
        elif last_name_range:
            names = set(widget.tag_names(last_name_range[0]))
            names.difference_update(constants.NON_RECORD_IDENTITY_TAG_NAMES)
            index = None
            for name in names:
                if index is None:
                    index = widget.tag_ranges(name)[-1]
                elif widget.compare(widget.tag_ranges(name)[-1], ">", index):
                    index = widget.tag_ranges(name)[-1]
            if index is None:
                index = tkinter.END
        else:
            tkinter.messagebox.showinfo(
                message="No field for FINISH field to be after"
            )
            return
        restore_insert = widget.index(tkinter.INSERT)
        widget.mark_set(tkinter.INSERT, index)
        if widget.get(tkinter.INSERT + "-1c") == "\n":
            content.insert_name_value_without_newline_prefix(
                widget, constants.FINISH, None, None
            )
        else:
            content.insert_name_value(widget, constants.FINISH, None, None)
        widget.mark_set(tkinter.INSERT, restore_insert)


def _get_start_next_range_tag_at_index(widget, tag, index):
    """Return start next range of tag from index."""
    nextrange = widget.tag_nextrange(tag, index)
    if nextrange:
        if widget.compare(nextrange[0], "==", index):
            nextrange = widget.tag_nextrange(tag, nextrange[1])
    if nextrange:
        return nextrange[0]
    return None


def _get_matching_tag_at_index(tags_widget_index, tag_names):
    """Return single tag of character at index which is in tag_names."""
    tags = tags_widget_index.intersection(tag_names)
    if len(tags) == 1:
        return tags.pop()
    if not tags:
        return None
    raise InserterError("More than one possible matching tag")


def _get_previous_matching_tag_at_index(widget, tag, tag_names, index):
    """Return tag at index if tag in tag_names and has previous range."""
    prevrange = widget.tag_prevrange(tag, index)
    if prevrange:
        if widget.compare(prevrange[1], ">=", index):
            prevrange = widget.tag_prevrange(tag, prevrange[0])
    if prevrange:
        return _get_matching_tag_at_index(
            set(widget.tag_names(prevrange[0])), tag_names
        )
    return None
