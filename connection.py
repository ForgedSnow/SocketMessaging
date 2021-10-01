from threading import Lock, Event, Thread
import json
import datetime


HOST = ""
PORT = 1212
BUFFER_SIZE = 1024
TIMEOUT = None


class Connection:
    def __init__(self, server_reference, host, port):
        self.server = server_reference
        self.host = host
        self.port = port

    def run(self):
        # assign player unique number
        id = self.server.assign_id()

        with server_reference.print_lock:
            print("User:", id, "has connected.")

        '''
        type 0: sender message datetime
        type 1: sender message
        type 2: array {matching type 0, .....}
        '''

        # send user they joined chat message
        send_data = json.dumps({"type": 0,
                                "sender": "Server",
                                "message": "You have successfully joined the channel",
                                "time": datetime.datetime.utcnow()})
        try:
            host.send(send_data.encode())
        except Exception:
            print("Client error. Disconnecting")
            return

        self.listening_thread = Thread(target=self.listen)
        self.listening = True
        self.listening_thread.start()

    def listen(self):
        while self.listening:
            raw = self.host.resv(BUFFER_SIZE)
            data = json.loads(raw.decode())
            if data.get("type") == 0:
                #handle message
                self.server.push_message(data.get("sender"), data.get("message"))