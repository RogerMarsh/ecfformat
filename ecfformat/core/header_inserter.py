# header_inserter.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Insert ECF results submission structure event detail elements into text."""

from . import inserter
from .sequences import HEADER_SEQUENCES

sequence_insert_map = {}
inserter.populate_sequence_insert_map(sequence_insert_map, HEADER_SEQUENCES)
del HEADER_SEQUENCES


class HeaderInserter(inserter.Inserter):
    """Build field structure for insertion into text at a chosen point.

    An inserter is created for the point at which insertion is chosen.

    The field structure is inserted after the current field, at the end of
    the current set of field, or at the end of the current part of the
    submission.

    """

    def verify_sequence_insert_map(self, map_from_subclass=None):
        """Append sequence_insert_map to map_from_subclass and delegate.

        sequence_insert_map is an attribute of header_inserter module.

        """
        map_from_subclass = self._verify_sequence_insert_map(
            sequence_insert_map, map_from_subclass=map_from_subclass
        )
        super().verify_sequence_insert_map(map_from_subclass=map_from_subclass)

    def _get_sequence_insert_map(self):
        """Delegate and append sequence_insert_map to returned list."""
        maps = super()._get_sequence_insert_map()
        maps.append(sequence_insert_map)
        return maps
