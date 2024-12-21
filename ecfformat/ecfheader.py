# ecfheader.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file header editor application."""

if __name__ == "__main__":

    from .ecfformat import APPLICATION_NAME
    from .ecfformat import check_solentware_misc_imports
    from .ecfformat import report_application_import_exception
    from .ecfformat import main

    APPLICATION_NAME = APPLICATION_NAME + " (Event Details)"

    check_solentware_misc_imports()
    try:
        from .gui.header import Header
    except (ImportError, SyntaxError) as error:
        report_application_import_exception(error)
    main(Header, APPLICATION_NAME)
