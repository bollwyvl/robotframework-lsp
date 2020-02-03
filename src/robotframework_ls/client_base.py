import logging
import itertools
from functools import partial

log = logging.getLogger(__name__)


def _read_into_queue(reader, queue):
    def _put_into_queue(msg):
        queue.put(msg)

    reader.listen(_put_into_queue)


class LanguageServerClientBase(object):
    """
    A base implementation for talking with a process that implements the language
    server.
    """

    TIMEOUT = None

    def __init__(self, writer, reader):
        """
        
        :param JsonRpcStreamWriter writer:
        :param JsonRpcStreamReader reader:
        """
        import threading

        try:
            from queue import Queue
        except:
            from Queue import Queue

        self.writer = writer
        self.reader = reader
        self._queue = Queue()

        t = threading.Thread(target=_read_into_queue, args=(reader, self._queue))
        t.start()
        self.require_exit_messages = True
        self.next_id = partial(next, itertools.count())

    def write(self, contents):
        self.writer.write(contents)

    def next_message(self, block=True, timeout=None):
        if timeout is None:
            timeout = self.TIMEOUT
        return self._queue.get(block=block, timeout=self.TIMEOUT)

    def wait_for_message(self, match):
        found = False
        while not found:
            msg = self.next_message()
            for key, value in match.items():
                if msg.get(key) == value:
                    continue

                log.info("Message found:\n%s\nwhile waiting for\n%s" % (msg, match))
                break
            else:
                found = True
        return msg

    def shutdown(self):
        self.write(
            {"jsonrpc": "2.0", "id": self.next_id(), "method": "shutdown",}
        )

    def exit(self):
        self.write(
            {"jsonrpc": "2.0", "id": self.next_id(), "method": "exit",}
        )
