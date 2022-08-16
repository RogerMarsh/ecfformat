# sequences.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Tables of keypress sequences, fields, records, and event handler methods.

Two tables are defined: HEADER_SEQUENCES for the event details part, and
SUBMISSION_SEQUENCES for the other parts, of an ECF results submission
file.  It would be reasonable to have separate tables for player list,
match results, other results, and section results, parts but the only split
needed at present is event details and the rest.

The sequences 'Alt-KeyPress-Delete' and 'Alt-KeyPress-Insert, and their menu
entry equivalents, are reserved for deleting fields and inserting an initial
EVENT DETAILS field.  The HEADER_SEQUENCES and SUBMISSION_SEQUENCES tables
do not cope with these delete and insert requirements.

"""

from . import constants
from . import fields


def method_name_suffix(description):
    """Return method name suffix for event handlers for description."""
    return "_".join(description[0].lower().split())


def _sib(name):
    return (name.capitalize(), (name,), frozenset((name,)))


def _sibtag(name):
    assert name in fields.tag_to_name
    return (fields.tag_to_name[name].capitalize(), (name,), frozenset((name,)))


def _sib_rep(name):
    return (name.capitalize(), (name,), frozenset())


def _sibtag_rep(name):
    assert name in fields.tag_to_name
    return (fields.tag_to_name[name].capitalize(), (name,), frozenset())


def _sib_exc(name, exclude_if_present):
    return (
        fields.tag_to_name.get(name, name).capitalize(),
        (name,),
        frozenset((name,)).union(exclude_if_present),
    )


def _sib_set(name, fieldnames):
    return (" ".join(_capitalize(*name)).strip(), fieldnames, frozenset())


def _sib_set_exc(name, fieldnames, exclude_if_present):
    return (name, fieldnames, frozenset(exclude_if_present))


def _capitalize(*strings):
    return tuple(string.capitalize() for string in strings)


# Sets of fields whose existence imply the option should not be available.
NGR = frozenset()
GED = frozenset((constants.EVENT_DETAILS,))
GPL = frozenset((constants.PLAYER_LIST,))
GFN = frozenset((constants.FINISH,))

TED = constants.EVENT_DETAILS
THP = constants.PIN1
TMR = constants.MATCH_RESULTS
TOR = constants.OTHER_RESULTS
TPL = constants.PLAYER_LIST
TPN = constants.PIN
TSR = constants.SECTION_RESULTS

OMPF = constants.ORDERED_MANDATORY_PIN1_FIELDS
T_NAME = (constants.NAME,)
HMR = (THP, TMR)
HOR = (THP, TOR)
HSR = (THP, TSR)
H_C = (constants.COLOUR,)
H_B = (constants.BOARD,)
H_G = (constants.GAME_DATE,)
H_R = (constants.ROUND,)
H_BC = (constants.BOARD, constants.COLOUR)
H_RC = (constants.ROUND, constants.COLOUR)
H_N_G = (constants.NAME_GAME_DATE,)
H_GBC = H_G + H_BC
H_GC = H_G + H_C
H_GB = H_G + H_B
H_GRC = H_G + H_RC
H_GR = H_G + H_R
H_N_GBC = H_N_G + H_BC
H_N_GC = H_N_G + H_C
H_N_GB = H_N_G + H_B
H_N_GRC = H_N_G + H_RC
H_N_GR = H_N_G + H_R

SIB_ED = _sibtag(TED)
SIB_MR = _sibtag_rep(constants.MATCH_RESULTS)
SIB_OR = _sibtag_rep(constants.OTHER_RESULTS)
SIB_SR = _sibtag_rep(constants.SECTION_RESULTS)
SIB_F = _sib(constants.FINISH)
SIB_C = _sib(constants.COLOUR)
SIB_S = _sib(constants.SCORE)
SIB_D = _sibtag(constants.GAME_DATE)
SIB_A = _sib(constants.PIN2)
SIB_H = _sib_rep(constants.PIN1)
SIB_CML = _sib(constants.COMMENT_LIST)
SIB_CMP = _sib(constants.COMMENT_PIN)
SIB_PIN = _sib(constants.PIN)
INHIBIT_EF = constants.MANDATORY_EVENT_FIELDS.union(
    constants.OPTIONAL_EVENT_FIELDS
).union(SIB_ED[-1])

FED = constants.EVENT_DETAILS_FIELD_TAGS.union({constants.EVENT_DETAILS})
FMH = constants.HPIN_MATCH_FIELD_TAGS.union({constants.PIN1})
FMR = frozenset(
    (
        constants.MATCH_RESULTS,
        constants.OTHER_RESULTS,
        constants.SECTION_RESULTS,
        constants.RESULTS_DATE,
        constants.WHITE_ON,
    )
)
FNONE = frozenset((None,))
FOH = constants.HPIN_OTHER_FIELD_TAGS.union({constants.PIN1})
FOR = frozenset(
    (
        constants.MATCH_RESULTS,
        constants.OTHER_RESULTS,
        constants.SECTION_RESULTS,
        constants.WHITE_ON,
    )
)
FPL = constants.PLAYER_LIST_FIELD_TAGS.union({constants.PLAYER_LIST})
FPN = constants.PIN_FIELD_TAGS.union({constants.PIN})
FSH = constants.HPIN_SECTION_FIELD_TAGS.union({constants.PIN1})
FSR = frozenset(
    (
        constants.MATCH_RESULTS,
        constants.OTHER_RESULTS,
        constants.SECTION_RESULTS,
        constants.RESULTS_DATE,
        constants.WHITE_ON,
    )
)
M1S = _sib_set_exc(
    "Mandatory 1 session",
    constants.ORDERED_MANDATORY_EVENT_FIELDS
    + constants.ORDERED_MANDATORY_1_SESSION,
    INHIBIT_EF,
)
M2S = _sib_set_exc(
    "Mandatory 2 session",
    constants.ORDERED_MANDATORY_EVENT_FIELDS
    + constants.ORDERED_MANDATORY_2_SESSION,
    INHIBIT_EF,
)
M3S = _sib_set_exc(
    "Mandatory 3 session",
    constants.ORDERED_MANDATORY_EVENT_FIELDS
    + constants.ORDERED_MANDATORY_3_SESSION,
    INHIBIT_EF,
)
MMS = _sib_set_exc(
    "Mandatory multi session",
    constants.ORDERED_MANDATORY_EVENT_FIELDS
    + constants.ORDERED_MANDATORY_MULTI_SESSION,
    INHIBIT_EF,
)
MNTLF = _sib_set_exc(
    "Mandatory no time limit fields",
    constants.ORDERED_MANDATORY_EVENT_FIELDS,
    INHIBIT_EF,
)
MNACC = _sib_set_exc(
    "Mandatory Name Club code",
    (constants.PIN, constants.NAME, constants.CLUB_CODE),
    (),
)
MNAEC = _sib_set_exc(
    "Mandatory Name ECF code",
    (constants.PIN, constants.NAME, constants.ECF_CODE),
    (),
)
MSACC = _sib_set_exc(
    "Mandatory Surname Club code",
    (constants.PIN, constants.SURNAME, constants.CLUB_CODE),
    (),
)
MSAEC = _sib_set_exc(
    "Mandatory Surname ECF code",
    (constants.PIN, constants.SURNAME, constants.ECF_CODE),
    (),
)
S_ADJ = _sib(constants.ADJUDICATED)
S_ICM = _sibtag(constants.INFORM_CHESSMOVES)
S_MIF = _sib_exc(
    constants.MINUTES_FIRST_SESSION,
    frozenset((constants.MINUTES_FOR_GAME,)),
)
S_MFG = _sib_exc(
    constants.MINUTES_FOR_GAME,
    frozenset((constants.ORDERED_MANDATORY_3_SESSION,)),
)
S_MRG = _sib_exc(
    constants.MINUTES_REST_OF_GAME,
    frozenset((constants.MINUTES_FOR_GAME,)),
)
S_MIS = _sib_exc(
    constants.MINUTES_SECOND_SESSION,
    frozenset((constants.MINUTES_FOR_GAME,)),
)
S_MOF = _sib_exc(
    constants.MOVES_FIRST_SESSION,
    frozenset((constants.MINUTES_FOR_GAME,)),
)
S_MOS = _sib_exc(
    constants.MOVES_SECOND_SESSION,
    frozenset((constants.MINUTES_FOR_GAME,)),
)
S_ROA = _sibtag_rep(constants.RESULTS_OFFICER_ADDRESS)
S_TRA = _sibtag_rep(constants.TREASURER_ADDRESS)
S_RDP = _sibtag(constants.RESULTS_DUPLICATED)
S_IFE = _sibtag(constants.INFORM_FIDE)
S_IUN = _sibtag(constants.INFORM_UNION)
S_FRD = _sibtag(constants.FINAL_RESULT_DATE)

HEADER_SEQUENCES = (
    # EVENT DETAILS sequences.
    ("<F1>", None, None, FNONE, SIB_ED, NGR),
    ("<Alt-F1>", None, None, FNONE, M2S, NGR),
    ("<Shift-F1>", None, None, FNONE, M1S, NGR),
    ("<Control-F1>", None, None, FNONE, MNTLF, NGR),
    ("<Control-Alt-F1>", None, None, FNONE, M3S, NGR),
    ("<Shift-Alt-F1>", None, None, FNONE, MMS, NGR),
    ("<F1>", TED, TED, FNONE, SIB_ED, GED),
    ("<Alt-F1>", TED, TED, FNONE, M2S, NGR),
    ("<Shift-F1>", TED, TED, FNONE, M1S, NGR),
    ("<Control-F1>", TED, TED, FNONE, MNTLF, NGR),
    ("<Control-Alt-F1>", TED, TED, FNONE, M3S, NGR),
    ("<Shift-Alt-F1>", TED, TED, FNONE, MMS, NGR),
    ("<F2>", TED, TED, FNONE, _sib(constants.ENVIRONMENT), NGR),
    ("<F3>", TED, TED, FNONE, _sibtag(constants.INFORM_GRAND_PRIX), NGR),
    ("<F4>", TED, TED, FNONE, _sibtag(constants.SECONDS_PER_MOVE), NGR),
    ("<Shift-Control-Alt-F2>", TED, TED, FNONE, S_ADJ, NGR),
    ("<Shift-Control-F2>", TED, TED, FNONE, S_IFE, NGR),
    ("<Shift-Alt-F2>", TED, TED, FNONE, S_ICM, NGR),
    ("<Control-Alt-F2>", TED, TED, FNONE, S_IUN, NGR),
    ("<Shift-F2>", TED, TED, FNONE, _sibtag(constants.EVENT_CODE), NGR),
    ("<Alt-F2>", TED, TED, FNONE, _sibtag(constants.SUBMISSION_INDEX), NGR),
    ("<Control-F2>", TED, TED, FNONE, _sibtag(constants.EVENT_NAME), NGR),
    ("<Shift-F4>", TED, TED, FNONE, S_MIF, NGR),
    ("<Alt-F4>", TED, TED, FNONE, S_MFG, NGR),
    ("<Control-F4>", TED, TED, FNONE, S_MRG, NGR),
    ("<Shift-Control-F4>", TED, TED, FNONE, S_MIS, NGR),
    ("<Shift-Alt-F4>", TED, TED, FNONE, S_MOF, NGR),
    ("<Control-Alt-F4>", TED, TED, FNONE, S_MOS, NGR),
    ("<Shift-F3>", TED, TED, FNONE, _sibtag(constants.EVENT_DATE), NGR),
    ("<Control-F3>", TED, TED, FNONE, S_FRD, NGR),
    ("<Alt-F3>", TED, TED, FNONE, _sibtag(constants.RESULTS_OFFICER), NGR),
    ("<Shift-Control-F3>", TED, TED, FNONE, S_ROA, NGR),
    ("<Shift-Alt-F3>", TED, TED, FNONE, _sib(constants.TREASURER), NGR),
    ("<Control-Alt-F3>", TED, TED, FNONE, S_TRA, NGR),
    ("<Shift-Control-Alt-F3>", TED, TED, FNONE, S_RDP, NGR),
    ("<Alt-F1>", TED, TED, FED, M2S, NGR),
    ("<Shift-F1>", TED, TED, FED, M1S, NGR),
    ("<Control-F1>", TED, TED, FED, MNTLF, NGR),
    ("<Control-Alt-F1>", TED, TED, FED, M3S, NGR),
    ("<Shift-Alt-F1>", TED, TED, FED, MMS, NGR),
    ("<F2>", TED, TED, FED, _sib(constants.ENVIRONMENT), NGR),
    ("<F3>", TED, TED, FED, _sibtag(constants.INFORM_GRAND_PRIX), NGR),
    ("<F4>", TED, TED, FED, _sibtag(constants.SECONDS_PER_MOVE), NGR),
    ("<Shift-Control-Alt-F2>", TED, TED, FED, S_ADJ, NGR),
    ("<Shift-Control-F2>", TED, TED, FED, S_IFE, NGR),
    ("<Shift-Alt-F2>", TED, TED, FED, S_ICM, NGR),
    ("<Control-Alt-F2>", TED, TED, FED, S_IUN, NGR),
    ("<Shift-F2>", TED, TED, FED, _sibtag(constants.EVENT_CODE), NGR),
    ("<Alt-F2>", TED, TED, FED, _sibtag(constants.SUBMISSION_INDEX), NGR),
    ("<Control-F2>", TED, TED, FED, _sibtag(constants.EVENT_NAME), NGR),
    ("<Shift-F4>", TED, TED, FED, S_MIF, NGR),
    ("<Alt-F4>", TED, TED, FED, S_MFG, NGR),
    ("<Control-F4>", TED, TED, FED, S_MRG, NGR),
    ("<Shift-Control-F4>", TED, TED, FED, S_MIS, NGR),
    ("<Shift-Alt-F4>", TED, TED, FED, S_MOF, NGR),
    ("<Control-Alt-F4>", TED, TED, FED, S_MOS, NGR),
    ("<Shift-F3>", TED, TED, FED, _sibtag(constants.EVENT_DATE), NGR),
    ("<Control-F3>", TED, TED, FED, S_FRD, NGR),
    ("<Alt-F3>", TED, TED, FED, _sibtag(constants.RESULTS_OFFICER), NGR),
    ("<Shift-Control-F3>", TED, TED, FED, S_ROA, NGR),
    ("<Shift-Alt-F3>", TED, TED, FED, _sib(constants.TREASURER), NGR),
    ("<Control-Alt-F3>", TED, TED, FED, S_TRA, NGR),
    ("<Shift-Control-Alt-F3>", TED, TED, FED, S_RDP, NGR),
)

SUBMISSION_SEQUENCES = (
    # EVENT DETAILS sequences.
    ("<F5>", TED, TED, FNONE, _sibtag(TPL), GPL),
    ("<F5>", TED, TED, FED, _sibtag(TPL), GPL),
    # PLAYER LIST sequences.
    ("<Alt-F5>", TPL, TPL, FPL, MNAEC, NGR),
    ("<Control-F5>", TPL, TPL, FPL, MSAEC, NGR),
    ("<Shift-F5>", TPL, TPL, FPL, MNACC, NGR),
    ("<Control-Alt-F5>", TPL, TPL, FPL, MSACC, NGR),
    ("<Shift-Control-Alt-F6>", TPL, TPL, FPL, SIB_CML, NGR),
    ("<F6>", TPL, TPL, FPL, SIB_PIN, NGR),
    # PIN sequences.
    ("<Alt-F5>", TPL, TPN, FPN, MNAEC, NGR),
    ("<Control-F5>", TPL, TPN, FPN, MSAEC, NGR),
    ("<Shift-F5>", TPL, TPN, FPN, MNACC, NGR),
    ("<Control-Alt-F5>", TPL, TPN, FPN, MSACC, NGR),
    ("<Shift-Control-Alt-F6>", TPL, TPN, FPN, SIB_CMP, NGR),
    ("<F6>", TPL, TPN, FPN, SIB_PIN, NGR),
    (
        "<Shift-Control-F6>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.BCF_CODE, (constants.ECF_CODE,)),
        NGR,
    ),
    (
        "<Shift-Alt-F6>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.BCF_NO, (constants.ECF_NO,)),
        NGR,
    ),
    (
        "<Shift-F7>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.ECF_CODE, (constants.BCF_CODE,)),
        NGR,
    ),
    (
        "<Shift-F8>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.ECF_NO, (constants.BCF_NO,)),
        NGR,
    ),
    (
        "<Control-F7>",
        TPL,
        TPN,
        FPN,
        _sib_exc(
            constants.NAME,
            (constants.SURNAME, constants.FORENAME, constants.INITIALS),
        ),
        NGR,
    ),
    (
        "<Shift-Control-F7>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.SURNAME, T_NAME),
        NGR,
    ),
    (
        "<Shift-Alt-F7>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.FORENAME, T_NAME),
        NGR,
    ),
    (
        "<Control-Alt-F7>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.INITIALS, T_NAME),
        NGR,
    ),
    (
        "<Control-Alt-F6>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.CLUB, (constants.CLUB_NAME,)),
        NGR,
    ),
    (
        "<Control-F8>",
        TPL,
        TPN,
        FPN,
        _sib_exc(constants.CLUB_NAME, (constants.CLUB,)),
        NGR,
    ),
    ("<Alt-F7>", TPL, TPN, FPN, _sibtag(constants.CLUB_CODE), NGR),
    ("<Shift-Alt-F8>", TPL, TPN, FPN, _sibtag(constants.CLUB_COUNTY), NGR),
    (
        "<Shift-Control-Alt-F8>",
        TPL,
        TPN,
        FPN,
        _sibtag(constants.DATE_OF_BIRTH),
        NGR,
    ),
    ("<Shift-Control-F8>", TPL, TPN, FPN, _sib(constants.TITLE), NGR),
    ("<Control-Alt-F8>", TPL, TPN, FPN, _sibtag(constants.FIDE_NO), NGR),
    ("<Alt-F8>", TPL, TPN, FPN, _sib(constants.GENDER), NGR),
    # MATCH RESULTS, OTHER RESULTS, and SECTION RESULTS, sequences.
    ("<Shift-F9>", TPL, TPL, FPL, SIB_MR, NGR),
    ("<Control-F9>", TPL, TPL, FPL, SIB_OR, NGR),
    ("<Alt-F9>", TPL, TPL, FPL, SIB_SR, NGR),
    ("<Shift-F9>", TPL, TPN, FPN, SIB_MR, NGR),
    ("<Control-F9>", TPL, TPN, FPN, SIB_OR, NGR),
    ("<Alt-F9>", TPL, TPN, FPN, SIB_SR, NGR),
    ("<Shift-F9>", TMR, TMR, FMR, SIB_MR, NGR),
    ("<Control-F9>", TMR, TMR, FMR, SIB_OR, NGR),
    ("<Alt-F9>", TMR, TMR, FMR, SIB_SR, NGR),
    (
        "<Control-w>",
        TMR,
        TMR,
        FMR - frozenset((constants.WHITE_ON,)),
        _sibtag(constants.WHITE_ON),
        NGR,
    ),
    (
        "<Control-Alt-d>",
        TMR,
        TMR,
        FMR - frozenset((constants.RESULTS_DATE,)),
        _sibtag(constants.RESULTS_DATE),
        NGR,
    ),
    (
        "<F12>",
        TMR,
        TMR,
        FMR,
        _sib_set(HMR + H_N_GBC, OMPF + H_GBC),
        NGR,
    ),
    (
        "<Alt-F12>",
        TMR,
        TMR,
        FMR,
        _sib_set(HMR + H_N_GC, OMPF + H_GC),
        NGR,
    ),
    (
        "<Control-F12>",
        TMR,
        TMR,
        FMR,
        _sib_set(HMR + H_BC, OMPF + H_BC),
        NGR,
    ),
    (
        "<Shift-F12>",
        TMR,
        TMR,
        FMR,
        _sib_set(HMR + H_C, OMPF + H_C),
        NGR,
    ),
    (
        "<Shift-Control-F12>",
        TMR,
        TMR,
        FMR,
        _sib_set(HMR + H_N_G, OMPF + H_G),
        NGR,
    ),
    (
        "<Control-Alt-F12>",
        TMR,
        TMR,
        FMR,
        _sib_set(HMR + H_B, OMPF + H_B),
        NGR,
    ),
    (
        "<Shift-Alt-F12>",
        TMR,
        TMR,
        FMR,
        _sib_set(HMR + ("",), OMPF),
        NGR,
    ),
    (
        "<Shift-Control-Alt-F12>",
        TMR,
        TMR,
        FMR,
        _sib_set(HMR + H_N_GB, OMPF + H_GB),
        NGR,
    ),
    ("<Shift-F9>", TOR, TOR, FOR, SIB_MR, NGR),
    ("<Control-F9>", TOR, TOR, FOR, SIB_OR, NGR),
    ("<Alt-F9>", TOR, TOR, FOR, SIB_SR, NGR),
    (
        "<Control-w>",
        TOR,
        TOR,
        FOR - frozenset((constants.WHITE_ON,)),
        _sibtag(constants.WHITE_ON),
        NGR,
    ),
    (
        "<F12>",
        TOR,
        TOR,
        FOR,
        _sib_set(HOR + H_N_GC, OMPF + H_GC),
        NGR,
    ),
    (
        "<Control-F12>",
        TOR,
        TOR,
        FOR,
        _sib_set(HOR + H_C, OMPF + H_C),
        NGR,
    ),
    (
        "<Control-Alt-F12>",
        TOR,
        TOR,
        FOR,
        _sib_set(HOR + ("",), OMPF),
        NGR,
    ),
    (
        "<Shift-Control-Alt-F12>",
        TOR,
        TOR,
        FOR,
        _sib_set(HOR + H_N_G, OMPF + H_G),
        NGR,
    ),
    ("<Shift-F9>", TSR, TSR, FSR, SIB_MR, NGR),
    ("<Control-F9>", TSR, TSR, FSR, SIB_OR, NGR),
    ("<Alt-F9>", TSR, TSR, FSR, SIB_SR, NGR),
    (
        "<Control-w>",
        TSR,
        TSR,
        FSR - frozenset((constants.WHITE_ON,)),
        _sibtag(constants.WHITE_ON),
        NGR,
    ),
    (
        "<Control-Alt-d>",
        TSR,
        TSR,
        FSR - frozenset((constants.RESULTS_DATE,)),
        _sibtag(constants.RESULTS_DATE),
        NGR,
    ),
    (
        "<F12>",
        TSR,
        TSR,
        FSR,
        _sib_set(HSR + H_N_GRC, OMPF + H_GRC),
        NGR,
    ),
    (
        "<Alt-F12>",
        TSR,
        TSR,
        FSR,
        _sib_set(HSR + H_N_GC, OMPF + H_GC),
        NGR,
    ),
    (
        "<Control-F12>",
        TSR,
        TSR,
        FSR,
        _sib_set(HSR + H_RC, OMPF + H_RC),
        NGR,
    ),
    (
        "<Shift-F12>",
        TSR,
        TSR,
        FSR,
        _sib_set(HSR + H_C, OMPF + H_C),
        NGR,
    ),
    (
        "<Shift-Control-F12>",
        TSR,
        TSR,
        FSR,
        _sib_set(HSR + H_N_G, OMPF + H_G),
        NGR,
    ),
    (
        "<Control-Alt-F12>",
        TSR,
        TSR,
        FSR,
        _sib_set(HSR + H_R, OMPF + H_R),
        NGR,
    ),
    (
        "<Shift-Alt-F12>",
        TSR,
        TSR,
        FSR,
        _sib_set(HSR + ("",), OMPF),
        NGR,
    ),
    (
        "<Shift-Control-Alt-F12>",
        TSR,
        TSR,
        FSR,
        _sib_set(HSR + H_N_GR, OMPF + H_GR),
        NGR,
    ),
    ("<Shift-F9>", TMR, THP, FMH, SIB_MR, NGR),
    ("<Control-F9>", TMR, THP, FMH, SIB_OR, NGR),
    ("<Alt-F9>", TMR, THP, FMH, SIB_SR, NGR),
    ("<Shift-F9>", TOR, THP, FOH, SIB_MR, NGR),
    ("<Control-F9>", TOR, THP, FOH, SIB_OR, NGR),
    ("<Alt-F9>", TOR, THP, FOH, SIB_SR, NGR),
    ("<Shift-F9>", TSR, THP, FSH, SIB_MR, NGR),
    ("<Control-F9>", TSR, THP, FSH, SIB_OR, NGR),
    ("<Alt-F9>", TSR, THP, FSH, SIB_SR, NGR),
    # PIN1 sequences.
    (
        "<F12>",
        TMR,
        THP,
        FMH,
        _sib_set(HMR + H_N_GBC, OMPF + H_GBC),
        NGR,
    ),
    (
        "<F12>",
        TOR,
        THP,
        FOH,
        _sib_set(HOR + H_N_GC, OMPF + H_GC),
        NGR,
    ),
    (
        "<F12>",
        TSR,
        THP,
        FSH,
        _sib_set(HSR + H_N_GRC, OMPF + H_GRC),
        NGR,
    ),
    (
        "<Alt-F12>",
        TMR,
        THP,
        FMH,
        _sib_set(HMR + H_N_GC, OMPF + H_GC),
        NGR,
    ),
    (
        "<Alt-F12>",
        TSR,
        THP,
        FSH,
        _sib_set(HSR + H_N_GC, OMPF + H_GC),
        NGR,
    ),
    (
        "<Control-F12>",
        TMR,
        THP,
        FMH,
        _sib_set(HMR + H_BC, OMPF + H_BC),
        NGR,
    ),
    (
        "<Control-F12>",
        TOR,
        THP,
        FOH,
        _sib_set(HOR + H_C, OMPF + H_C),
        NGR,
    ),
    (
        "<Control-F12>",
        TSR,
        THP,
        FSH,
        _sib_set(HSR + H_RC, OMPF + H_RC),
        NGR,
    ),
    (
        "<Shift-F12>",
        TMR,
        THP,
        FMH,
        _sib_set(HMR + H_C, OMPF + H_C),
        NGR,
    ),
    (
        "<Shift-F12>",
        TSR,
        THP,
        FSH,
        _sib_set(HSR + H_C, OMPF + H_C),
        NGR,
    ),
    (
        "<Shift-Control-F12>",
        TMR,
        THP,
        FMH,
        _sib_set(HMR + H_N_G, OMPF + H_G),
        NGR,
    ),
    (
        "<Shift-Control-F12>",
        TSR,
        THP,
        FSH,
        _sib_set(HSR + H_N_G, OMPF + H_G),
        NGR,
    ),
    (
        "<Control-Alt-F12>",
        TMR,
        THP,
        FMH,
        _sib_set(HMR + H_B, OMPF + H_B),
        NGR,
    ),
    (
        "<Control-Alt-F12>",
        TOR,
        THP,
        FOH,
        _sib_set(HOR + ("",), OMPF),
        NGR,
    ),
    (
        "<Control-Alt-F12>",
        TSR,
        THP,
        FSH,
        _sib_set(HSR + H_R, OMPF + H_R),
        NGR,
    ),
    (
        "<Shift-Alt-F12>",
        TMR,
        THP,
        FMH,
        _sib_set(HMR + ("",), OMPF),
        NGR,
    ),
    (
        "<Shift-Alt-F12>",
        TSR,
        THP,
        FSH,
        _sib_set(HSR + ("",), OMPF),
        NGR,
    ),
    (
        "<Shift-Control-Alt-F12>",
        TMR,
        THP,
        FMH,
        _sib_set(HMR + H_N_GB, OMPF + H_GB),
        NGR,
    ),
    (
        "<Shift-Control-Alt-F12>",
        TOR,
        THP,
        FOH,
        _sib_set(HOR + H_N_G, OMPF + H_G),
        NGR,
    ),
    (
        "<Shift-Control-Alt-F12>",
        TSR,
        THP,
        FSH,
        _sib_set(HSR + H_N_GR, OMPF + H_GR),
        NGR,
    ),
    (
        "<Control-b>",
        TMR,
        THP,
        FMH - frozenset((constants.BOARD,)),
        _sib(constants.BOARD),
        NGR,
    ),
    (
        "<Control-c>",
        TMR,
        THP,
        FMH - frozenset((constants.COLOUR,)),
        SIB_C,
        NGR,
    ),
    (
        "<Control-d>",
        TMR,
        THP,
        FMH - frozenset((constants.GAME_DATE,)),
        SIB_D,
        NGR,
    ),
    (
        "<Control-h>",
        TMR,
        THP,
        FMH - frozenset((constants.PIN1,)),
        SIB_H,
        NGR,
    ),
    (
        "<Control-a>",
        TMR,
        THP,
        FMH - frozenset((constants.PIN2,)),
        SIB_A,
        NGR,
    ),
    (
        "<Control-equal>",
        TMR,
        THP,
        FMH - frozenset((constants.SCORE,)),
        SIB_S,
        NGR,
    ),
    (
        "<Control-c>",
        TOR,
        THP,
        FOH - frozenset((constants.COLOUR,)),
        SIB_C,
        NGR,
    ),
    (
        "<Control-d>",
        TOR,
        THP,
        FOH - frozenset((constants.GAME_DATE,)),
        SIB_D,
        NGR,
    ),
    (
        "<Control-h>",
        TOR,
        THP,
        FOH - frozenset((constants.PIN1,)),
        SIB_H,
        NGR,
    ),
    (
        "<Control-a>",
        TOR,
        THP,
        FOH - frozenset((constants.PIN2,)),
        SIB_A,
        NGR,
    ),
    (
        "<Control-equal>",
        TOR,
        THP,
        FOH - frozenset((constants.SCORE,)),
        SIB_S,
        NGR,
    ),
    (
        "<Control-c>",
        TSR,
        THP,
        FSH - frozenset((constants.COLOUR,)),
        SIB_C,
        NGR,
    ),
    (
        "<Control-d>",
        TSR,
        THP,
        FSH - frozenset((constants.GAME_DATE,)),
        SIB_D,
        NGR,
    ),
    (
        "<Control-h>",
        TSR,
        THP,
        FSH - frozenset((constants.PIN1,)),
        SIB_H,
        NGR,
    ),
    (
        "<Control-a>",
        TSR,
        THP,
        FSH - frozenset((constants.PIN2,)),
        SIB_A,
        NGR,
    ),
    (
        "<Control-r>",
        TSR,
        THP,
        FSH - frozenset((constants.ROUND,)),
        _sib(constants.ROUND),
        NGR,
    ),
    (
        "<Control-equal>",
        TSR,
        THP,
        FSH - frozenset((constants.SCORE,)),
        SIB_S,
        NGR,
    ),
    # FINISH sequences.
    ("<Shift-Control-Alt-F5>", TED, TED, FNONE, SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TED, TED, FED, SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TPL, TPL, FPL, SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TPL, TPN, FPN, SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TMR, TMR, frozenset((TMR,)), SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TOR, TOR, frozenset((TOR,)), SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TSR, TSR, frozenset((TSR,)), SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TMR, THP, FMH, SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TOR, THP, FOH, SIB_F, GFN),
    ("<Shift-Control-Alt-F5>", TSR, THP, FSH, SIB_F, GFN),
)

# Delete scaffold for HEADER_SEQUENCES and SUBMISSION_SEQUENCES.
del NGR, GED, GPL, GFN
del TED, FED, FNONE, TPL, FPL, TPN
del FPN, FMH, FMR, FOH, FOR, FSH, FSR
del THP, TMR, TOR, TSR
del M2S, M1S, MNTLF
del M3S, MMS, MNAEC, MSAEC, MNACC, MSACC
del SIB_ED, SIB_F, SIB_C, SIB_S, SIB_D, SIB_A, SIB_H
del INHIBIT_EF
del SIB_MR, SIB_OR, SIB_SR, SIB_CML, SIB_CMP, SIB_PIN
del OMPF
del T_NAME
del HMR, HOR, HSR
del H_GBC, H_N_GBC, H_GC, H_N_GC, H_BC, H_C, H_G, H_N_G, H_B, H_GB, H_N_GB
del H_GRC, H_N_GRC, H_RC, H_R, H_GR, H_N_GR
del S_ADJ, S_FRD, S_ICM, S_IFE, S_IUN, S_MIF, S_MOF, S_MOS, S_MFG, S_MIS
del S_MRG, S_RDP, S_ROA, S_TRA
del _sib, _sib_exc, _sib_rep, _sib_set, _sib_set_exc, _sibtag, _sibtag_rep
del _capitalize, constants, fields
