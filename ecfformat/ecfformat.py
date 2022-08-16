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
try:
    from solentware_misc.gui.startstop import stop_application
except (ImportError, SyntaxError) as sa_exception:
    stop_application = False
try:
    from solentware_misc.gui.startstop import application_exception
except (ImportError, SyntaxError) as ss_exception:
    application_exception = False

APPLICATION_NAME = None
try:
    from . import APPLICATION_NAME
except ImportError as an_exception:
    APPLICATION_NAME = False


def check_solentware_misc_imports():
    """Report solentware_misc import failures then raise SystemExit."""
    if start_application_exception is False:
        tkinter.messagebox.showerror(
            title="Start Exception",
            message=".\n\nThe reported exception is:\n\n".join(
                (
                    "Unable to import start_application_exception module",
                    str(sae_exception),
                )
            ),
        )
        raise SystemExit(
            "Unable to import start application utilities"
        ) from sae_exception
    if stop_application is False:
        tkinter.messagebox.showerror(
            title="Start Exception",
            message=".\n\nThe reported exception is:\n\n".join(
                (
                    "Unable to import stop_application module",
                    str(sa_exception),
                )
            ),
        )
        raise SystemExit(
            "Unable to import start application utilities"
        ) from sa_exception
    if application_exception is False:
        tkinter.messagebox.showerror(
            title="Start Exception",
            message=".\n\nThe reported exception is:\n\n".join(
                (
                    "Unable to import application_exception module",
                    str(application_exception),
                )
            ),
        )
        raise SystemExit(
            "Unable to import start application utilities"
        ) from ss_exception
    if APPLICATION_NAME is False:
        tkinter.messagebox.showerror(
            title="Start Exception",
            message=".\n\nThe reported exception is:\n\n".join(
                (
                    "Unable to import application_name",
                    str(an_exception),
                )
            ),
        )
        raise SystemExit("Unable to import application name") from an_exception


def report_application_import_exception():
    """Report application import failure then raise SystemExit."""
    start_application_exception(
        ai_error, appname=APPLICATION_NAME, action="import"
    )
    raise SystemExit(
        " import ".join(("Unable to", APPLICATION_NAME))
    ) from ai_error


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
        report_application_import_exception()
    main(Submission, APPLICATION_NAME)
