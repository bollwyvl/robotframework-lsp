import logging
import os.path
import sys

__file__ = os.path.abspath(__file__)
log = logging.getLogger(__name__)

_critical_error_log_file = os.path.join(
    os.path.expanduser("~"), "robotframework_server_api_critical.log"
)


def start_server_process(args=()):
    """
    Calls this __main__ in another process.
    
    :param args:
        The list of arguments for the server process. 
        i.e.:
            ["-vv", "--log-file=%s" % log_file]
    """
    import subprocess

    language_server_process = subprocess.Popen(
        [sys.executable, "-u", __file__] + list(args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )

    return language_server_process


if __name__ == "__main__":
    try:
        log.info("Initializing RobotFramework Server api. Args: %s", (sys.argv[1:],))
        from robotframework_ls import __main__
        from robotframework_ls.ext.server import RobotFrameworkServerApi

        __main__.main(language_server_class=RobotFrameworkServerApi)
    except:
        # Critical error (the logging may not be set up properly).
        import traceback

        # Print to file and stderr.
        with open(_critical_error_log_file, "a+") as stream:
            traceback.print_exc(file=stream)

        traceback.print_exc()
