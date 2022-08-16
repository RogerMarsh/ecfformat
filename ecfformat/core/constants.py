# constants.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Constants used in generating and parsing ECF results submission files.

These are the field names, separators, and the standard values for the
fields which have them.

"""
RECENT_RESULTS_FORMAT_FILE = "resultsformatfile"
SHOW_VALUE_BOUNDARY = "showvalueboundary"
SHOW_VALUE_BOUNDARY_TRUE = "True"
SHOW_VALUE_BOUNDARY_FALSE = "False"
CHECK_NAME_COUNT = "checknamecount"
CHECK_NAME_COUNT_TRUE = "True"
CHECK_NAME_COUNT_FALSE = "False"

#
# It is also hoped that "zero_not_0" is a sufficiently unusual value that
# it will not be used by other grading programs as a valid PIN separate
# from "0".  Thus avoiding problems that may arise from the conventional
# use of "zero_not_0" by this program to cope with the ECF submission file
# conventional use of "0".
ECF_RESULT_0D = "0d"
ECF_RESULT_D0 = "d0"
ECF_COLOUR_WHITE = "white"
ECF_COLOUR_BLACK = "black"
ECF_COLOUR_W = "w"
ECF_COLOUR_B = ""
ECF_COLOURDEFAULT_ALL = "all"
ECF_COLOURDEFAULT_EVEN = "even"
ECF_COLOURDEFAULT_NONE = "none"
ECF_COLOURDEFAULT_ODD = "odd"
ECF_COLOURDEFAULT_UNKNOWN = "unknown"
ECF_ZERO_NOT_0 = "zero_not_0"

# Field names at ecfrating.org.uk/doc/spec/field_def.html dated 15 April 2022.
# CLUB NAME is in file layout but not field definition.  It is in the field
# definition file at 20 December 2014 (date stamp on my copy).
# RESULTS DUPLICATED has disappeared since 20 December 2014.
# Spaces are removed from the published values because the specification
# states 'spaces are ignored in field names'.  These values are used as the
# tkinter tag names and are mapped to the names in the specification for
# display and submission file content.
# Tcl/Tk and tkinter tag names for fields.
# The ECF field names which include space characters should have tag names
# without space characters.
ADJUDICATED = "ADJUDICATED"  # Accepted but ignored.
BCF_CODE = "BCFCODE"  # alias for "ECF CODE" which has replaced it.
BCF_NO = "BCFNO"  # alias for "ECF NO" which has replaced it.
BOARD = "BOARD"
CLUB = "CLUB"  # alias for "CLUB NAME", missing in file layout and field spec.
CLUB_CODE = "CLUBCODE"
CLUB_COUNTY = "CLUBCOUNTY"
CLUB_NAME = "CLUBNAME"  # missing but exists in file layout.
COLOUR = "COLOUR"
COLUMN = "COLUMN"  # not used but must be recognised.
COMMENT = "COMMENT"  # not used but must be recognised.
COMMENT_LIST = "COMMENTLIST"  # Tag name for COMMENT field before PIN fields.
COMMENT_PIN = "COMMENTPIN"  # Tag name for COMMENT field in PIN fieldset.
DATE_OF_BIRTH = "DATEOFBIRTH"  # not used but must be recognised.
ECF_CODE = "ECFCODE"
ECF_NO = "ECFNO"
ENVIRONMENT = "ENVIRONMENT"
EVENT_CODE = "EVENTCODE"
EVENT_DATE = "EVENTDATE"
EVENT_DETAILS = "EVENT"
EVENT_NAME = "EVENTNAME"
FIDE_NO = "FIDENO"
FINAL_RESULT_DATE = "FINALRESULTDATE"
FINISH = "FINISH"
FORENAME = "FORENAME"  # NAME is used in preference.
GAME_DATE = "GAMEDATE"
GENDER = "GENDER"
INFORM_FIDE = "INFORMFIDE"  # Accepted but ignored.
INFORM_CHESSMOVES = "INFORMCHESSMOVES"  # Accepted but ignored.
INFORM_GRAND_PRIX = "INFORMGRANDPRIX"
INFORM_UNION = "INFORMUNION"  # Accepted but ignored.
INITIALS = "INITIALS"  # NAME is used in preference.
MATCH_RESULTS = "MATCH"
MINUTES_FIRST_SESSION = "MINUTESFIRSTSESSION"
MINUTES_FOR_GAME = "MINUTESFORGAME"
MINUTES_REST_OF_GAME = "MINUTESRESTOFGAME"
MINUTES_SECOND_SESSION = "MINUTESSECONDSESSION"
MOVES_FIRST_SESSION = "MOVESFIRSTSESSION"
MOVES_SECOND_SESSION = "MOVESSECONDSESSION"
NAME = "NAME"
OTHER_RESULTS = "OTHER"
PIN = "PIN"

# Avoid numeric suffix ambiguity for PIN, PIN1, and PIN2, field names.
PIN1 = "HPIN"
PIN2 = "APIN"

PLAYER_LIST = "PLAYER"
RESULTS_DATE = "RESULTSDATE"
RESULTS_DUPLICATED = "RESULTSDUPLICATED"  # Gone since 20 December 2014.
RESULTS_OFFICER = "RESULTSOFFICER"
RESULTS_OFFICER_ADDRESS = "RESULTSOFFICERADDRESS"
ROUND = "ROUND"
SCORE = "SCORE"
SECONDS_PER_MOVE = "SECONDSPERMOVE"
SECTION_RESULTS = "SECTION"
SUBMISSION_INDEX = "SUBMISSIONINDEX"
SURNAME = "SURNAME"  # NAME is used in preference.
TABLE_START = "TABLESTART"  # not used but must be recognised.
TABLE_END = "TABLEEND"  # not used but must be recognised.
TITLE = "TITLE"
TREASURER = "TREASURER"
TREASURER_ADDRESS = "TREASURERADDRESS"
WHITE_ON = "WHITEON"

# It is convenient to assume a field name "" for processing the values
# presented between the TABLE START and TABLE END fields like
# '#<value>#'.
TABLE_VALUE = ""

# Used in validation of ECF codes, formerly Grading codes.
GRADING_CODE_LENGTH = 7
GRADING_CODE_CHECK_CHARACTERS = "ABCDEFGHJKL"

# ECF NO is formally prefixed by "ME", but commonly left out.
# ECF NO is the ECF membership number.
ECF_NO_PREFIX = "ME"

# Field delimiters.
# FIELD_SEPARATOR separates <name value> pairs.
# NAME_VALUE_SEPARATOR is the separator between name and value.
FIELD_SEPARATOR = "#"
NAME_VALUE_SEPARATOR = "="

NAME_ONLY_FIELDS = frozenset((EVENT_DETAILS, FINISH, PLAYER_LIST))
SUBPART_TAGS = frozenset((PIN, PIN1))
PART_TAGS = frozenset(
    (
        EVENT_DETAILS,
        FINISH,
        MATCH_RESULTS,
        PLAYER_LIST,
        OTHER_RESULTS,
        SECTION_RESULTS,
    )
)

# The parts which may contain fields in sets marked by fields in SUBPART_TAGS.
# PIN goes in PLAYER_LIST and PIN1 goes in the rest.
RECORD_TAGS = frozenset(
    (
        MATCH_RESULTS,
        PLAYER_LIST,
        OTHER_RESULTS,
        SECTION_RESULTS,
    )
)

# The parts where the '(#COLUMN=<value>)+#TABLE START(#<value>)*#TABLE END'
# construct may be present in files generated externally.
TABLE_TYPES = RECORD_TAGS

# These field tag names mark the points where stopping parsing makes sense:
# they end the previous part of the file.  For the *RESULTS fields it is the
# first one found that matters.
PARSE_STOP_AT_FIELDS = PART_TAGS

# FIELDS_ALLOWED_* tuples refer to COMMENT, not COMMENT_LIST or COMMENT_PIN.
# Mappings between ECF and internal field names deal with the differences
# between the comment definitions and, for example, ECF_NO and NAME_ECF_NO.
FIELDS_ALLOWED_IN_MATCH = (
    PIN1,
    PIN2,
    SCORE,
    COLOUR,
    BOARD,
    GAME_DATE,
    COMMENT,
)
FIELDS_ALLOWED_IN_OTHER = (PIN1, PIN2, SCORE, COLOUR, GAME_DATE, COMMENT)
FIELDS_ALLOWED_IN_SECTION = (
    PIN1,
    PIN2,
    SCORE,
    COLOUR,
    ROUND,
    GAME_DATE,
    COMMENT,
)
FIELDS_ALLOWED_IN_PLAYERS = (
    PIN,
    ECF_CODE,
    NAME,
    SURNAME,
    FORENAME,
    INITIALS,
    GENDER,
    TITLE,
    DATE_OF_BIRTH,
    CLUB_CODE,
    CLUB_NAME,
    CLUB_COUNTY,
    ECF_NO,
    FIDE_NO,
    COMMENT,
    BCF_CODE,
    BCF_NO,
    CLUB,
)

PIN_SET_TERMINATORS = (
    COLUMN,
    FINISH,
    MATCH_RESULTS,
    OTHER_RESULTS,
    SECTION_RESULTS,
)
PIN1_SET_TERMINATORS = PIN_SET_TERMINATORS
PLAYERS_SET_TERMINATORS = PIN_SET_TERMINATORS

# Display names for field names where the tag name is concatenated words or
# mangled for uniqueness when digit sufficies are appended.
NAME_BCF_CODE = "BCF CODE"
NAME_BCF_NO = "BCF NO"
NAME_CLUB_CODE = "CLUB CODE"
NAME_CLUB_COUNTY = "CLUB COUNTY"
NAME_CLUB_NAME = "CLUB NAME"
NAME_COMMENT = "COMMENT"  # For COMMENT_LIST anf COMMENT_PIN tags.
NAME_DATE_OF_BIRTH = "DATE OF BIRTH"
NAME_ECF_CODE = "ECF CODE"
NAME_ECF_NO = "ECF NO"
NAME_EVENT_CODE = "EVENT CODE"
NAME_EVENT_DATE = "EVENT DATE"
NAME_EVENT_DETAILS = "EVENT DETAILS"
NAME_EVENT_NAME = "EVENT NAME"
NAME_FIDE_NO = "FIDE NO"
NAME_FINAL_RESULT_DATE = "FINAL RESULT DATE"
NAME_GAME_DATE = "GAME DATE"
NAME_INFORM_FIDE = "INFORM FIDE"
NAME_INFORM_CHESSMOVES = "INFORM CHESSMOVES"
NAME_INFORM_GRAND_PRIX = "INFORM GRAND PRIX"
NAME_INFORM_UNION = "INFORM UNION"
NAME_MATCH_RESULTS = "MATCH RESULTS"
NAME_MINUTES_FIRST_SESSION = "MINUTES FIRST SESSION"
NAME_MINUTES_FOR_GAME = "MINUTES FOR GAME"
NAME_MINUTES_REST_OF_GAME = "MINUTES REST OF GAME"
NAME_MINUTES_SECOND_SESSION = "MINUTES SECOND SESSION"
NAME_MOVES_FIRST_SESSION = "MOVES FIRST SESSION"
NAME_MOVES_SECOND_SESSION = "MOVES SECOND SESSION"
NAME_OTHER_RESULTS = "OTHER RESULTS"
NAME_PIN1 = "PIN1"
NAME_PIN2 = "PIN2"
NAME_PLAYER_LIST = "PLAYER LIST"
NAME_RESULTS_DATE = "RESULTS DATE"
NAME_RESULTS_DUPLICATED = "RESULTS DUPLICATED"
NAME_RESULTS_OFFICER = "RESULTS OFFICER"
NAME_RESULTS_OFFICER_ADDRESS = "RESULTS OFFICER ADDRESS"
NAME_SECONDS_PER_MOVE = "SECONDS PER MOVE"
NAME_SECTION_RESULTS = "SECTION RESULTS"
NAME_SUBMISSION_INDEX = "SUBMISSION INDEX"
NAME_TABLE_START = "TABLE START"
NAME_TABLE_END = "TABLE END"
NAME_TREASURER_ADDRESS = "TREASURER ADDRESS"
NAME_WHITE_ON = "WHITE ON"

TAG_NAMES = frozenset(
    (
        ADJUDICATED,
        BOARD,
        CLUB,
        COLOUR,
        COLUMN,
        COMMENT,  # outside PLAYER LIST and PIN fieldsets only.
        COMMENT_LIST,  # inside PLAYER LIST fieldset before first PIN only.
        COMMENT_PIN,  # inside PIN fieldset only.
        ENVIRONMENT,
        FINISH,
        FORENAME,
        GENDER,
        INITIALS,
        NAME,
        PIN,
        PIN1,
        PIN2,
        ROUND,
        SCORE,
        SURNAME,
        TITLE,
        TREASURER,
        BCF_CODE,
        BCF_NO,
        CLUB_CODE,
        CLUB_COUNTY,
        CLUB_NAME,
        DATE_OF_BIRTH,
        ECF_CODE,
        ECF_NO,
        EVENT_CODE,
        EVENT_DATE,
        EVENT_DETAILS,
        EVENT_NAME,
        FIDE_NO,
        FINAL_RESULT_DATE,
        GAME_DATE,
        INFORM_FIDE,
        INFORM_CHESSMOVES,
        INFORM_GRAND_PRIX,
        INFORM_UNION,
        MATCH_RESULTS,
        MINUTES_FIRST_SESSION,
        MINUTES_FOR_GAME,
        MINUTES_REST_OF_GAME,
        MINUTES_SECOND_SESSION,
        MOVES_FIRST_SESSION,
        MOVES_SECOND_SESSION,
        OTHER_RESULTS,
        PLAYER_LIST,
        RESULTS_DATE,
        RESULTS_DUPLICATED,
        RESULTS_OFFICER,
        RESULTS_OFFICER_ADDRESS,
        SECONDS_PER_MOVE,
        SECTION_RESULTS,
        SUBMISSION_INDEX,
        TABLE_START,
        TABLE_END,
        TREASURER_ADDRESS,
        WHITE_ON,
    )
)

PART_AND_SUBPART_TAG_NAMES = (
    (EVENT_DETAILS,),
    (PLAYER_LIST, PIN),
    (MATCH_RESULTS, PIN1),
    (OTHER_RESULTS, PIN1),
    (SECTION_RESULTS, PIN1),
)

# The status for field names, except tables related fields and fields allowed
# as first field, which are known and expected.
STATUS_OK = "ok"

# The status for ignoring a field.
STATUS_IGNORE = "ignore"

# The status for starting a table for the defined columns.
STATUS_TABLE_START = "table_start"

# The status for collecting a table value for a table.
STATUS_TABLE_VALUE = "table_value"

# The status for ending a table.
STATUS_TABLE_END = "table_end"

# The status for collecting table column names.
STATUS_COLUMN = "column"

# Status values for fields with some kind of error.
# Named TAG_* because these are used as tags.
TAG_ERROR_UNKNOWN = "unknown"
TAG_ERROR_UNEXPECTED = "unexpected"
TAG_ERROR_TABLE_LAYOUT = "layout"

ERROR_TAG_NAMES = frozenset(
    (
        TAG_ERROR_TABLE_LAYOUT,
        TAG_ERROR_UNEXPECTED,
        TAG_ERROR_UNKNOWN,
    )
)

# The tag names of fields which must appear after the EVENT DETAILS field
# and before the PLAYER LIST field.
ORDERED_MANDATORY_EVENT_FIELDS = (
    EVENT_CODE,
    SUBMISSION_INDEX,
    EVENT_NAME,
    EVENT_DATE,
    FINAL_RESULT_DATE,
    RESULTS_OFFICER,
    RESULTS_OFFICER_ADDRESS,
    TREASURER,
    TREASURER_ADDRESS,
)
MANDATORY_EVENT_FIELDS = frozenset(ORDERED_MANDATORY_EVENT_FIELDS)

# One of these time limit field combinations is mandatory in event details.
ORDERED_MANDATORY_1_SESSION = (MINUTES_FOR_GAME,)
ORDERED_MANDATORY_2_SESSION = (
    MOVES_FIRST_SESSION,
    MINUTES_FIRST_SESSION,
    MINUTES_REST_OF_GAME,
)
ORDERED_MANDATORY_MULTI_SESSION = (
    MOVES_FIRST_SESSION,
    MINUTES_FIRST_SESSION,
    MOVES_SECOND_SESSION,
    MINUTES_SECOND_SESSION,
)
ORDERED_MANDATORY_3_SESSION = ORDERED_MANDATORY_MULTI_SESSION + (
    MINUTES_REST_OF_GAME,
)

# The tag names of optional fields which may appear after the EVENT DETAILS
# field and before the PLAYER LIST field.  These are the time limit fields
# and some optional or ignored fields; including RESULTS DUPLICATED which
# was removed from the ECF submission format around 2014.
OPTIONAL_EVENT_FIELDS = frozenset(
    ORDERED_MANDATORY_1_SESSION
    + ORDERED_MANDATORY_3_SESSION
    + (ENVIRONMENT, INFORM_GRAND_PRIX, SECONDS_PER_MOVE)
    + (ADJUDICATED, INFORM_CHESSMOVES, INFORM_FIDE, INFORM_UNION)
    + (RESULTS_DUPLICATED,)
)

# The tag names of fields which must appear after a PIN1 field and before
# the next PIN1 field (or *RESULTS field if it is last one in *RESULTS set).
ORDERED_MANDATORY_PIN1_FIELDS = (
    PIN1,
    SCORE,
    PIN2,
)
MANDATORY_PIN1_FIELDS = frozenset(ORDERED_MANDATORY_PIN1_FIELDS)

# NAME is the preferred field but SURNAME, INITIALS, and FORENAME, are
# allowed too.
ALTERNATIVE_NAME_FIELDS = frozenset(
    (
        NAME,
        SURNAME,
    )
)
FORENAME_INITIAL_FIELDS = frozenset(
    (
        FORENAME,
        INITIALS,
    )
)

# The tag for all field names in '#<name>[=<value>]#' instances.
FIELD_NAME_TAG = "name"

# The tag for all field values in '#[<name>=]<value>]' instances.
FIELD_VALUE_TAG = "value"

FIELD_TAG_NAMES = frozenset(
    (
        FIELD_NAME_TAG,
        FIELD_VALUE_TAG,
    )
)

# tkinter does not support the 'displaychars' option of the Text widget's
# get command.
# The displaychars option was introduced at Tcl/Tk 8.5 so most recent
# Python's could support it assuming they use Tcl/Tk 8.5 or later.
# The non-elided characters are those not associated with the tag 'elided'.
# If possible these characters will be found by inverting relevant ranges of
# characters with the tag 'elided'.  Also it may be convenient to not elide
# the characters with the tag 'elided', just ignore them where appropriate.
# Thus no need to hack support for the displaychars option of tk Text get
# command.
UI_VALUE_BOUNDARY_TAG = "bound"
BOUNDARY = " "

# The colour highlight tags for the field under the insert cursor.
UI_NAME_HIGHLIGHT_TAG = "colorname"
UI_VALUE_HIGHLIGHT_TAG = "colorvalue"

UI_TAG_NAMES = frozenset(
    (
        UI_VALUE_BOUNDARY_TAG,
        UI_NAME_HIGHLIGHT_TAG,
        UI_VALUE_HIGHLIGHT_TAG,
    )
)

# Tag names which are not record and part identity or type tags.
NON_RECORD_NAME_TAG_NAMES = UI_TAG_NAMES.union(FIELD_TAG_NAMES).union(
    ERROR_TAG_NAMES
)

# Tag names which are not record and part identity tags.
NON_RECORD_IDENTITY_TAG_NAMES = TAG_NAMES.union(NON_RECORD_NAME_TAG_NAMES)

TAGS_START_NEWLINE = (
    frozenset(
        (
            EVENT_DETAILS,
            FINISH,
            MATCH_RESULTS,
            OTHER_RESULTS,
            PLAYER_LIST,
            SECTION_RESULTS,
            PIN,
            PIN1,
            WHITE_ON,
            RESULTS_DATE,
            TABLE_START,
            TABLE_END,
            COLUMN,
        )
    )
    .union(MANDATORY_EVENT_FIELDS)
    .union(OPTIONAL_EVENT_FIELDS)
)

# Names used as keys in tk Text dump() return values.
TK_TEXT_DUMP_TEXT = "text"
TK_TEXT_DUMP_MARK = "mark"
TK_TEXT_DUMP_TAGON = "tagon"
TK_TEXT_DUMP_TAGOFF = "tagoff"
TK_TEXT_DUMP_IMAGE = "image"
TK_TEXT_DUMP_WINDOW = "window"

EVENT_DETAILS_FIELD_TAGS = frozenset(
    (
        ENVIRONMENT,
        INFORM_GRAND_PRIX,
        EVENT_CODE,
        SUBMISSION_INDEX,
        EVENT_NAME,
        EVENT_DATE,
        FINAL_RESULT_DATE,
        RESULTS_OFFICER,
        RESULTS_OFFICER_ADDRESS,
        TREASURER,
        TREASURER_ADDRESS,
        MINUTES_FIRST_SESSION,
        MINUTES_FOR_GAME,
        MINUTES_REST_OF_GAME,
        MINUTES_SECOND_SESSION,
        MOVES_FIRST_SESSION,
        MOVES_SECOND_SESSION,
        SECONDS_PER_MOVE,
        INFORM_FIDE,
        INFORM_CHESSMOVES,
        INFORM_UNION,
        ADJUDICATED,
        RESULTS_DUPLICATED,
    )
)

PLAYER_LIST_FIELD_TAGS = frozenset((COMMENT_LIST,))
PIN_FIELD_TAGS = frozenset(
    (
        COMMENT_PIN,
        ECF_CODE,
        NAME,
        SURNAME,
        FORENAME,
        INITIALS,
        GENDER,
        TITLE,
        DATE_OF_BIRTH,
        CLUB_CODE,
        CLUB_NAME,
        CLUB_COUNTY,
        ECF_NO,
        FIDE_NO,
        CLUB,
        BCF_CODE,
        BCF_NO,
    )
)
HPIN_MATCH_FIELD_TAGS = frozenset(
    (
        PIN2,
        SCORE,
        COLOUR,
        BOARD,
        GAME_DATE,
    )
)
HPIN_OTHER_FIELD_TAGS = frozenset(
    (
        PIN2,
        SCORE,
        COLOUR,
        GAME_DATE,
    )
)
HPIN_SECTION_FIELD_TAGS = frozenset(
    (
        PIN2,
        SCORE,
        COLOUR,
        ROUND,
        GAME_DATE,
    )
)
