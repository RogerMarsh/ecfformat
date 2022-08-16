# taggedcontent.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""The content of an ECF results submission file deconstructed by tag."""

from . import constants
from . import builder


class TaggedContentError(Exception):
    """Exception class for taggedcontent module."""


class TaggedHeaderContent(builder.Builder):
    """The data structure of the header in an ECF results submission file.

    An event header must have one of each field in event_details, and is
    allowed more than one of each field in event_details_at_least_one.

    An event header must have exactly one of each field in one of the sets
    from each of environments and time_limits.  Note this means the
    ENVIRONMENT field is optional and it's value defaults to 'OTB'.

    The ECF ignores the fields in event_details_ignored, but these are
    accepted in submissions for historical reasons (in other words they
    were used at some time in the past).

    """

    def parse(self, widget, stop_at=constants.PLAYER_LIST):
        """Split text into fields and validate field structure."""
        return super().parse(widget, stop_at=stop_at)


class TaggedContent(TaggedHeaderContent):
    """The data structure of an ECF results submission file.

    The description of RESULTS DATE in the field definition is not
    consistent with the description of it's use under the overall structure
    heading in the file layout.  However the description under result
    details is consistent.  Best to avoid this field.

    WHITE ON and COMMENT are best avoided too, though COMMENT has no per
    result alternative.

    The field definition for COMMENT is inconsistent with the file layout
    descriptions of it's use.  In particular the file layout descriptions
    do not support the example use in the field definitions.

    """

    def parse(self, widget, stop_at=constants.FINISH):
        """Split text into fields and validate field structure."""
        return super().parse(widget, stop_at=stop_at)
