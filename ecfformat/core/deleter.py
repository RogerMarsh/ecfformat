# deleter.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Remove ECF results submission structure elements from text."""

import tkinter

from . import constants


def _delete_event_details(widget, name, start, end):
    """Delete EVENT DETAILS part.

    The '-1c' modifier includes the '#' preceding the field name.

    """
    del name
    event_range = widget.tag_nextrange(constants.EVENT_DETAILS, end)
    if not event_range:
        return (widget.index(start + "-1c"), tkinter.END)
    return (widget.index(start + "-1c"), event_range[0] + "-1c")


def _delete_player_list(widget, name, start, end):
    """Delete PLAYER LIST part.

    The '-1c' modifier includes the '#' preceding the field name.

    """
    del name
    event_range = widget.tag_nextrange(constants.EVENT_DETAILS, end)
    finish_range = widget.tag_nextrange(constants.FINISH, end)
    if not event_range and not finish_range:
        return (widget.index(start + "-1c"), tkinter.END)
    if event_range and finish_range:
        if widget.compare(event_range[0], "<", finish_range[0]):
            return (start + "-1c", event_range[0] + "-1c")
    if finish_range:
        return (start + "-1c", finish_range[-1])
    return (start + "-1c", event_range[0] + "-1c")


def _delete_part_or_fieldset_field_name(widget, name, start, end):
    """Delete fields assiated with a part or fieldset field name.

    The '-1c' modifier includes the '#' preceding the field name.

    """
    del widget, name
    return (start + "-1c", end)


def _delete_field(widget, name, *args):
    """Delete <name> field in part or fieldset.

    The '-1c' modifier includes the '#' preceding the field name.

    """
    del args
    fieldname_range = widget.tag_prevrange(name, tkinter.INSERT)
    before = widget.tag_nextrange(constants.FIELD_NAME_TAG, tkinter.INSERT)
    if before:
        before = before[0]
    else:
        before = tkinter.END
    value_range = widget.tag_prevrange(
        constants.FIELD_VALUE_TAG, before, fieldname_range[-1]
    )
    if value_range:
        after = value_range[-1]
    else:
        after = before + "-1c"
    return (fieldname_range[0] + "-1c", after)


_delete_part_or_fieldset = {
    constants.EVENT_DETAILS: _delete_event_details,
    constants.FINISH: _delete_part_or_fieldset_field_name,
    constants.MATCH_RESULTS: _delete_part_or_fieldset_field_name,
    constants.PLAYER_LIST: _delete_player_list,
    constants.OTHER_RESULTS: _delete_part_or_fieldset_field_name,
    constants.SECTION_RESULTS: _delete_part_or_fieldset_field_name,
    constants.PIN: _delete_part_or_fieldset_field_name,
    constants.PIN1: _delete_part_or_fieldset_field_name,
}


def delete_fields(widget):
    """Delete part, fieldset, or field, at insert point in widget."""
    index = widget.index(tkinter.INSERT)
    tag_names = set(widget.tag_names(index))
    if constants.FIELD_NAME_TAG not in tag_names:
        return
    tag_names.remove(constants.FIELD_NAME_TAG)
    name = tag_names.intersection(constants.TAG_NAMES)
    if not name:
        return
    tag_names.difference_update(
        name.union(constants.NON_RECORD_NAME_TAG_NAMES)
    )
    if len(tag_names) < 1 or len(tag_names) > 2:
        return
    name = name.pop()
    start = None
    end = None
    while tag_names:
        range_name = tag_names.pop()
        range_ = widget.tag_nextrange(range_name, "1.0")
        if range_ and (start is None or widget.compare(range_[0], ">", start)):
            start = range_[0]
        range_ = widget.tag_prevrange(range_name, tkinter.END)
        if range_ and (end is None or widget.compare(range_[-1], "<", end)):
            end = range_[-1]
    delete_range = _delete_part_or_fieldset.get(name, _delete_field)(
        widget, name, start, end
    )

    # Unset marks from high to low with offset +1c on character delete range.
    start, end = [index + "+1c" for index in delete_range]
    mark = widget.mark_previous(end)
    while True:
        if not mark or widget.compare(mark, "<", start):
            break
        mark_current = mark
        mark = widget.mark_previous(mark)
        if mark_current.startswith(constants.FIELD_VALUE_TAG):
            widget.mark_unset(mark_current)

    # Do not delete trailing newline in field value.
    if widget.get(delete_range[-1] + "-1c") == "\n":
        delete_range = (
            delete_range[0],
            widget.index(delete_range[-1] + "-1c"),
        )

    widget.delete(*delete_range)

    # There will be a '\n\n' sequence if only field on line, other than first,
    # was deleted: remove first '\n'.
    delete_range = (delete_range[0], delete_range[0] + "+2c")
    if widget.get(*delete_range) == "\n\n":
        widget.delete(delete_range[0])
