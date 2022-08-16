# submission_inserter.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Insert ECF results submission player and game elements into text."""

from . import header_inserter
from .inserter import populate_sequence_insert_map
from .sequences import SUBMISSION_SEQUENCES

sequence_insert_map = {}
populate_sequence_insert_map(sequence_insert_map, SUBMISSION_SEQUENCES)
del populate_sequence_insert_map


class SubmissionInserter(header_inserter.HeaderInserter):
    """Build field structure for insertion into text at a chosen point.

    An inserter is created for the point at which insertion is chosen.

    The field structure is inserted after the current field, at the end of
    the current set of field, or at the end of the current part of the
    submission.

    """

    # _get_sequence_insert_map is defined before verify_sequence_insert_map
    # rather than after to avoid a duplicate code report by pylint, when
    # compared with the header_inserter module layout.
    # sequence_insert_map is a module attribute, and even factoring out the
    # append by 'self.add(maps, super()._get_sequence_insert_map())' does
    # not help.
    def _get_sequence_insert_map(self):
        """Delegate and append sequence_insert_map to returned list."""
        maps = super()._get_sequence_insert_map()
        maps.append(sequence_insert_map)
        return maps

    def verify_sequence_insert_map(self, map_from_subclass=None):
        """Append sequence_insert_map to map_from_subclass and delegate.

        sequence_insert_map is an attribute of submission_inserter module.

        """
        map_from_subclass = self._verify_sequence_insert_map(
            sequence_insert_map, map_from_subclass=map_from_subclass
        )
        super().verify_sequence_insert_map(map_from_subclass=map_from_subclass)
