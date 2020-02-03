# Copyright 2017 Palantir Technologies, Inc.
# License: MIT

import logging.config
import argparse
import sys
import os

log = logging.getLogger(__name__)


LOG_FORMAT = "%(asctime)s UTC - %(levelname)s - %(name)s\n%(message)s\n\n"

_critical_error_log_file = os.path.join(
    os.path.expanduser("~"), "robotframework_ls_critical.log"
)


def _critical_msg(msg):
    with open(_critical_error_log_file, "a+") as stream:
        stream.write(msg + "\n")


def add_arguments(parser):
    parser.description = "Python Language Server"

    parser.add_argument(
        "--tcp", action="store_true", help="Use TCP server instead of stdio"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    parser.add_argument("--port", type=int, default=1456, help="Bind to this port")
    parser.add_argument(
        "--check-parent-process",
        action="store_true",
        help="Check whether parent process is still alive using os.kill(ppid, 0) "
        "and auto shut down language server process when parent process is not alive."
        "Note that this may not work on a Windows machine.",
    )

    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        "--log-config", help="Path to a JSON file containing Python logging config."
    )
    log_group.add_argument(
        "--log-file",
        help="Redirect logs to the given file instead of writing to stderr."
        "Has no effect if used with --log-config.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity of log output, overrides log config file",
    )


def main(args=None, after_bind=lambda server: None, language_server_class=None):
    try:
        import robotframework_ls
    except ImportError:
        # Automatically add it to the path if __main__ is being executed.
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import robotframework_ls  # @UnusedImport

    from robotframework_ls.python_ls import (
        start_io_lang_server,
        start_tcp_lang_server,
        binary_stdio,
    )

    if language_server_class is None:
        from robotframework_ls.robotframework_ls_impl import (
            RobotFrameworkLanguageServer,
        )

        language_server_class = RobotFrameworkLanguageServer

    parser = argparse.ArgumentParser()
    add_arguments(parser)

    args = parser.parse_args(args=args if args is not None else sys.argv[1:])
    _configure_logger(args.verbose, args.log_config, args.log_file)

    if args.tcp:
        start_tcp_lang_server(
            args.host, args.port, language_server_class, after_bind=after_bind,
        )
    else:
        stdin, stdout = binary_stdio()
        start_io_lang_server(stdin, stdout, language_server_class)


def _configure_logger(verbose=0, log_config=None, log_file=None):
    if getattr(_configure_logger, "called", False):
        return  # i.e.: in dev mode we may call multiple times
    _configure_logger.called = True

    root_logger = logging.root

    if log_config:
        import json

        with open(log_config, "r") as f:
            logging.config.dictConfig(json.load(f))
    else:
        formatter = logging.Formatter(LOG_FORMAT)
        if log_file:
            log_file = os.path.expanduser(log_file)
            log_handler = logging.handlers.RotatingFileHandler(
                log_file,
                mode="a",
                maxBytes=50 * 1024 * 1024,
                backupCount=10,
                encoding=None,
                delay=0,
            )
        else:
            log_handler = logging.StreamHandler()
        log_handler.setFormatter(formatter)
        root_logger.addHandler(log_handler)

    if verbose == 0:
        level = logging.CRITICAL
    elif verbose == 1:
        level = logging.WARNING
    elif verbose >= 2:
        level = logging.DEBUG

    root_logger.setLevel(level)


if __name__ == "__main__":
    try:
        log.info("Initializing Language Server. Args: %s", (sys.argv[1:],))

        main()
    except:
        # Critical error (the logging may not be set up properly).
        import traceback

        # Print to file and stderr.
        with open(_critical_error_log_file, "a+") as stream:
            traceback.print_exc(file=stream)

        traceback.print_exc()
