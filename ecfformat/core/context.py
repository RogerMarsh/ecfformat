# context.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""The ECF results submission field structure at a point in a file.

The structure lists the part types surrounding a point, identifiers for the
instances of these types at the point, and the sibling fields present in the
innermost instance.

The context may become inaccurate after modification of the file.

The intended use is determine the context at the nominal insert point,
insert stuff, discard the context.

The actual insert point may not be the nominal insert point: more likely
being after the field, record, or part, containing the nominal insert
point.  The nominal insert point is usually tkinter.INSERT at the time of
the request.

Parts start with one of the field names EVENT DETAILS, PLAYER LIST,
MATCH RESULTS, OTHER RESULTS, SECTION RESULTS, and FINISH.

Records start with one of the field names PIN and PIN1.

PIN records occur in the PLAYER LIST part.

PIN1 records occur in the MATCH RESULTS, OTHER RESULTS, and SECTION RESULTS,
parts.

All part and record types have a set of fields allowed within instances, but
that set is empty for the FINISH part.

Fields in a part do not belong in any record within the part and must be
before any records within the part.

"""

import collections


Context = collections.namedtuple(
    "Context", ["part", "record", "field", "part_id", "record_id", "siblings"]
)
Context.__doc__ += ": ECF results submission field context."
Context.part.__doc__ = "The part type."
Context.record.__doc__ = "The sub-part, or record, type."
Context.field.__doc__ = "The field type."
Context.part_id.__doc__ = "The identifier for the part in this context."
Context.record_id.__doc__ = "The identifier for the record in this context."
Context.siblings.__doc__ = "The existing fields in the current record."
