# ecfformat.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results submission file editor application."""

import tkinter.messagebox

# start_application_exception = None
# stop_application = None
# application_exception = None

try:
    from solentware_misc.gui.startstop import start_application_exception
except (ImportError, SyntaxError) as sae_exception:
    start_application_exception = False
    SAE_MESSAGE = str(sae_exception)
try:
    from solentware_misc.gui.startstop import stop_application
except (ImportError, SyntaxError) as sa_exception:
    stop_application = False
    SA_MESSAGE = str(sa_exception)
try:
    from solentware_misc.gui.startstop import application_exception
except (ImportError, SyntaxError) as ss_exception:
    application_exception = False
    SS_MESSAGE = str(ss_exception)

APPLICATION_NAME = None
try:
    from . import APPLICATION_NAME
except ImportError as an_exception:
    APPLICATION_NAME = False
    AN_MESSAGE = str(an_exception)

if start_application_exception is False:
    SAE_MESSAGE = None
if start_application_exception is False:
    SA_MESSAGE = None
if start_application_exception is False:
    SS_MESSAGE = None
if start_application_exception is False:
    AN_MESSAGE = None


def check_solentware_misc_imports():
    """Report solentware_misc import failures then raise SystemExit."""
    if start_application_exception is False:
        tkinter.messagebox.showerror(
            title="Start Exception",
            message=".\n\nThe reported exception is:\n\n".join(
                (
                    "Unable to import start_application_exception module",
                    SAE_MESSAGE,
                )
            ),
        )
        raise SystemExit("Unable to import start application utilities")
    if stop_application is False:
        tkinter.messagebox.showerror(
            title="Start Exception",
            message=".\n\nThe reported exception is:\n\n".join(
                (
                    "Unable to import stop_application module",
                    SA_MESSAGE,
                )
            ),
        )
        raise SystemExit("Unable to import start application utilities")
    if application_exception is False:
        tkinter.messagebox.showerror(
            title="Start Exception",
            message=".\n\nThe reported exception is:\n\n".join(
                (
                    "Unable to import application_exception module",
                    SS_MESSAGE,
                )
            ),
        )
        raise SystemExit("Unable to import start application utilities")
    if APPLICATION_NAME is False:
        tkinter.messagebox.showerror(
            title="Start Exception",
            message=".\n\nThe reported exception is:\n\n".join(
                (
                    "Unable to import application_name",
                    AN_MESSAGE,
                )
            ),
        )
        raise SystemExit("Unable to import application name")


def report_application_import_exception(error):
    """Report application import failure then raise SystemExit."""
    start_application_exception(
        error, appname=APPLICATION_NAME, action="import"
    )
    raise SystemExit(
        " import ".join(("Unable to", APPLICATION_NAME))
    ) from error


def main(main_class, application_name):
    """Run application.

    The exceptions caught as tk_error are raised in tkinter.__init__ module.

    SystemExit is raised in tkinter.__init__ too, but Control-c can be used
    to stop application and would be intercepted anyway.

    """
    try:
        app = main_class(
            application_name=application_name, title=application_name
        )
    except Exception as sa_error:
        start_application_exception(
            sa_error, appname=application_name, action="initialise"
        )
        raise SystemExit(
            " initialise ".join(("Unable to", application_name))
        ) from sa_error
    try:
        app.root.mainloop()
    except SystemExit:
        stop_application(app, app.root)
        raise SystemExit from None
    except (RuntimeError, TypeError, ValueError, tkinter.TclError) as tk_error:
        application_exception(
            tk_error,
            app,
            app.root,
            title=application_name,
            appname=application_name,
        )


if __name__ == "__main__":

    check_solentware_misc_imports()
    try:
        from .gui.submission import Submission
    except (ImportError, SyntaxError) as ai_error:
        report_application_import_exception(ai_error)
    main(Submission, APPLICATION_NAME)
