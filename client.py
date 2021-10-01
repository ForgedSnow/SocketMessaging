import socket
from threading import Lock, Thread, Event
import json


BUFFER_SIZE = 1024
print_lock = Lock()


class Client:
    def __init__(self):
        self.serving_requests = True
        self.connect()

    def connect(self):
        host = "127.0.0.1"
        port = 1212

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting...")
        try:
            s.connect((host, port))
            print("Connected")
        except ConnectionRefusedError:
            print("Cannot connect to host (%s:%s)" % (host, port))
            return

        listening_thread = Thread(target=self.listening_loop, args=[s])
        listening_thread.start()

        self.sending_loop(s)
        listening_thread.join()

    def sending_loop(self, s):
        while self.serving_requests:
            message = input()
            try:
                send_data = json.dumps({"type": "client_message", "message": message})
                s.send(send_data.encode())
            except ConnectionRefusedError:
                with print_lock:
                    print("Connection rejected by host")
                self.serving_requests = False
                break

    def listening_loop(self, s):
        while self.serving_requests:
            try:
                data_raw = s.recv(BUFFER_SIZE)
                data = json.loads(data_raw.decode())
                time = data.get("time")
                with print_lock:
                    print("%s:%s %s:\n%s" % (time[0], time[1], data.get("sender"), data.get("message")))
            except ConnectionResetError:
                with print_lock:
                    print("Connection closed by host")
                self.serving_requests = False
                break


if __name__ == "__main__":
    client = Client()
