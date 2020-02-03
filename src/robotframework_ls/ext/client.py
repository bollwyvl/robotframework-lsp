from robotframework_ls.client_base import LanguageServerClientBase


class RobotFrameworkApiClient(LanguageServerClientBase):
    def initialize(self, msg_id=None, process_id=None):
        msg_id = msg_id if msg_id is not None else self.next_id()
        self.write(
            {
                "jsonrpc": "2.0",
                "id": msg_id,
                "method": "initialize",
                "params": {"processId": process_id,},
            }
        )

        msg = self.wait_for_message({"id": msg_id})
        return msg
