from robotframework_ls import _utils
from robotframework_ls.python_ls import PythonLanguageServer
import threading
import logging


log = logging.getLogger(__name__)

LINT_DEBOUNCE_S = 0.5  # 500 ms


class RobotFrameworkLanguageServer(PythonLanguageServer):
    def __init__(self, rx, tx):
        PythonLanguageServer.__init__(self, rx, tx)

        self._server_process = None
        self._server_api = None
        self._server_lock = threading.RLock()

    def _get_server_api(self):
        import os

        if self._server_process is None:
            with self._server_lock:
                # Check again with lock.
                if self._server_process is None:
                    try:
                        from robotframework_ls.options import Setup
                        from robotframework_ls.ext.client import RobotFrameworkApiClient
                        from robotframework_ls.ext.server__main__ import (
                            start_server_process,
                        )
                        from pyls_jsonrpc.streams import JsonRpcStreamWriter
                        from pyls_jsonrpc.streams import JsonRpcStreamReader

                        args = []
                        if Setup.options.verbose:
                            args.append("-" + "v" * int(Setup.options.verbose))
                        if Setup.options.log_file:
                            args.append("--log-file=" + Setup.options.log_file + ".api")

                        server_process = start_server_process(args=args)

                        self._server_process = server_process

                        write_to = server_process.stdin
                        read_from = server_process.stdout
                        w = JsonRpcStreamWriter(write_to, sort_keys=True)
                        r = JsonRpcStreamReader(read_from)

                        self._server_api = RobotFrameworkApiClient(w, r, server_process)
                        self._server_api.initialize(process_id=os.getpid())
                    except Exception as e:
                        log.exception(
                            "Error starting robotframework server api. Base exception: %s. Stderr: %s"
                            % (e, server_process.stderr.read())
                        )

        return self._server_api

    def m_shutdown(self, **_kwargs):
        with self._server_lock:
            if self._server_api is not None:
                self._server_api.shutdown()

        PythonLanguageServer.m_shutdown(self, **_kwargs)

    def m_exit(self, **_kwargs):
        with self._server_lock:
            if self._server_api is not None:
                self._server_api.exit()
        PythonLanguageServer.m_exit(self, **_kwargs)

    @_utils.debounce(LINT_DEBOUNCE_S, keyed_by="doc_uri")
    def lint(self, doc_uri, is_saved):
        # Since we're debounced, the document may no longer be open
        workspace = self._match_uri_to_workspace(doc_uri)
        if doc_uri in workspace.documents:
            document = workspace.get_document(doc_uri)

            source = document.source
            server_api = self._get_server_api()
            if server_api is not None:
                found = []
                diagnostics_msg = server_api.lint(source)
                if diagnostics_msg:
                    found = diagnostics_msg.get("result", [])
                workspace.publish_diagnostics(doc_uri, found)
