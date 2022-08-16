# miscellaneous.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file editor utility methods.

Methods which are not specific to subclasses of Menus, such as Header or
Submissions, but not needed by Menus are put in the Miscellaneous class.

The Submission class could reasonably have been a direct subclass of Menus,
not via Header, and stuff needed by both has to be somewhere.  Menus is a
suitable place but the default "too many lines" limit of pylint, 1000, is
breached if done that way.

"""

import tkinter

from . import menus
from ..core import constants
from ..core import fields


class MiscellaneousError(Exception):
    """Exception class for miscellaneous module."""


class Miscellaneous(menus.Menus):
    """Define methods needed by one or more other subclasses of Menus."""

    def _value_range_containing_mark(self, index):
        """Return value range containing mark index or None."""
        widget = self.widget
        range_ = widget.tag_prevrange(constants.FIELD_VALUE_TAG, index)
        if (
            range_
            and widget.compare(range_[0], "<=", index)
            and widget.compare(range_[1], ">=", index)
        ):
            return range_
        character = widget.get(index + "-1c")
        tag_names = widget.tag_names(index + "-1c")
        if self.content.value_edge:
            if (
                tag_names
                and character == constants.BOUNDARY
                and tag_names[0] == constants.UI_VALUE_BOUNDARY_TAG
            ):
                range_ = widget.tag_nextrange(constants.FIELD_VALUE_TAG, index)
                if range_ and widget.compare(range_[0], "==", index):
                    return range_
        if not tag_names and character == constants.NAME_VALUE_SEPARATOR:
            range_ = widget.tag_nextrange(constants.FIELD_VALUE_TAG, index)
            if range_ and widget.compare(range_[0], "==", index):
                return range_
        return None

    def _value_range_containing_insert_mark(self):
        """Return value range containing insert mark or None."""
        return self._value_range_containing_mark(tkinter.INSERT)

    def _value_range_nearest_mark(self, index):
        """Return value range nearest mark index or None.

        Previous range is chosen as nearest before next range if insert
        mark is not within a value range.

        """
        widget = self.widget
        tag_names = widget.tag_names(index)
        for tag in tag_names:
            if tag == constants.FIELD_VALUE_TAG:
                return self._value_range_containing_mark(index)
        range_ = widget.tag_prevrange(constants.FIELD_VALUE_TAG, index)
        if range_:
            return range_
        range_ = widget.tag_nextrange(constants.FIELD_VALUE_TAG, index)
        if range_:
            return range_
        return None

    def _value_range_nearest_insert_mark(self):
        """Return value range nearest insert mark or None."""
        return self._value_range_nearest_mark(tkinter.INSERT)

    def _value_range_nearest_current_mark(self):
        """Return value range nearest curren mark or None."""
        return self._value_range_nearest_mark(tkinter.CURRENT)

    def _get_part_record_field_types_and_names_for_value(self, index):
        """Return tuple part and record types and names, and field type.

        index is assumed to be a location with the 'value' tag, which may
        not have an associated value nor any associated field instances.

        Format is (part-type, record-type, field-type, part-name, record-name).

        The names are the types with a numeric suffix.  The part, record, and
        field, type identifiers may be the same.

        """
        widget = self.widget
        value_names = set(widget.tag_names(index)).difference(
            constants.NON_RECORD_IDENTITY_TAG_NAMES
        )
        range_ = widget.tag_prevrange(constants.FIELD_NAME_TAG, index)
        if not range_:
            return None
        name_names = set(widget.tag_names(range_[0])).difference(
            constants.NON_RECORD_NAME_TAG_NAMES
        )
        part_names, insert_names = fields.get_identity_tags_for_names(
            widget, value_names.copy(), range_[0]
        )
        record_id = value_names.intersection(name_names).intersection(
            insert_names
        )
        part_id = record_id.intersection(part_names)
        record_id.difference_update(part_id)
        record = insert_names.difference(part_names)
        if not record:
            record = insert_names.difference(value_names)
            record.discard(constants.FIELD_NAME_TAG)
            record.discard(constants.UI_NAME_HIGHLIGHT_TAG)
            part = set(record)
        else:
            record = record.difference(value_names)
            record.discard(constants.UI_NAME_HIGHLIGHT_TAG)
            part = part_names.difference(insert_names)
        field = name_names.difference(insert_names)
        if not field:
            field = set(record)
        else:
            field = field.difference(value_names)
            field.discard(constants.FIELD_NAME_TAG)
        for item in (part_id, record, field, part):
            if len(item) != 1:
                return None
        part_id = part_id.pop()
        if record_id:
            record_id = record_id.pop()
        else:
            record_id = part_id
        part = part.pop()
        record = record.pop()
        siblings = self._get_existing_fields_in_record(part, record, record_id)
        return (part, record, field.pop(), part_id, record_id, siblings)

    def _get_bindings_context_after_up_or_down(self):
        """Set KeyPress and popup menu bindings for field at index."""
        return self._get_part_record_field_types_and_names_for_value(
            tkinter.INSERT
        )

    def _get_part_record_field_types_and_names_for_name(self, index):
        """Return tuple part and record types and names, and field type.

        index is assumed to be a location with the 'name' tag, which may
        not have an associated value nor any associated field instances.

        Format is (part-type, record-type, field-type, part-name, record-name).

        The names are the types with a numeric suffix.  The part, record, and
        field, type identifiers may be the same.

        """
        widget = self.widget
        tag_names = set(widget.tag_names(index))
        if constants.FIELD_NAME_TAG not in tag_names:
            return None
        tag_names.remove(constants.FIELD_NAME_TAG)
        part = tag_names.intersection(constants.PART_TAGS)
        if len(part) == 1:
            identity_tag_names = tag_names.difference(
                part.union(constants.NON_RECORD_NAME_TAG_NAMES)
            )
            # Need exactly one name for picking record_id and field, where
            # record_id will be part_id too.
            # In some badly constructed files there will be no names (a file
            # starting with a valid sequence of COLUMN, TABLE START, value,
            # and TABLE END, fields; followed by a valid OTHER RESULTS
            # sequence, and FINISH, fields for example).
            # Maybe it is possible to get more than two names.
            # Probably difficult to give a coherent explanation of field
            # traversal behaviour across all cases: but crashes are avoided
            # in what can reasonably described as random field sequences
            # compared with the expected field structure.
            if len(identity_tag_names) != 1:
                return None
            record_id = identity_tag_names.pop()
            part = part.pop()
            if part in constants.RECORD_TAGS:
                field = part
            else:
                field = None
            siblings = self._get_existing_fields_in_record(
                part, part, record_id
            )
            return (part, part, field, record_id, record_id, siblings)
        range_ = widget.tag_nextrange(constants.FIELD_VALUE_TAG, index)
        if not range_:
            return None
        return self._get_part_record_field_types_and_names_for_value(range_[0])

    def _get_existing_fields_in_record(self, part, record, record_id):
        """Return field names present in record."""
        names = set()
        widget = self.widget
        field_name_tag = constants.FIELD_NAME_TAG
        key = (part, record)
        if key not in self._allowed_inserts:
            return names
        allowed = self._allowed_inserts[key].union(record)
        index = "1.0"
        while True:
            range_ = widget.tag_nextrange(record_id, index)
            if not range_:
                break
            range_names = set(widget.tag_names(range_[0]))
            if field_name_tag not in range_names:
                index = range_[1]
                continue
            found = set()
            for name in range_names:
                if name in allowed:
                    found.add(name)
            found.discard(record)
            assert len(found) < 2
            names.update(found)
            index = range_[1]
        return names

    def _get_bindings_context_after_control_up_or_down(self):
        """Return KeyPress and popup menu bindings for field at index."""
        return self._get_part_record_field_types_and_names_for_name(
            tkinter.INSERT
        )

    def _get_bindings_context_after_buttonpress(self):
        """Return binding descriptions for field at current mark."""
        # Assume Double and Triple ButtonPress-1 events are disabled to
        # avoid false detection of a change in context.
        tag_names = set(self.widget.tag_names(tkinter.CURRENT))
        if tag_names.intersection(constants.FIELD_TAG_NAMES):
            return self._get_part_record_field_types_and_names_for_value(
                tkinter.CURRENT
            )
        return None

    # Should this be like 'after_buttonpress' or 'control_up_or_down'?
    def _get_bindings_context_at_insert_mark(self):
        """Return binding descriptions for field at insert mark."""
        tag_names = set(self.widget.tag_names(tkinter.INSERT))
        if constants.FIELD_NAME_TAG in tag_names:
            return self._get_part_record_field_types_and_names_for_name(
                tkinter.INSERT
            )
        if constants.FIELD_VALUE_TAG in tag_names:
            return self._get_part_record_field_types_and_names_for_value(
                tkinter.INSERT
            )
        return None

    def _define_scrolling_event_and_command_handlers(self, actions):
        """Define event and command handlers for widget navigation.

        The method names derived from actions must not duplicate names from
        sequences module.

        The two *_<derived name> methods are alternative ways of invoking
        the _handle_<derived name> method.

        """
        for item in actions:
            suffix = item[1]
            handler = "_handle_" + suffix
            assert hasattr(self, handler)
            self._define_event_handler(suffix, handler)
            self._define_command_handler(suffix, handler)
