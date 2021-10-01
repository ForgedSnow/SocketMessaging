import socket
from threading import Lock, Thread, Event
import json


BUFFER_SIZE = 1024


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

        #recieving loop
        while self.serving_requests:
            try:
                data_raw = s.recv(BUFFER_SIZE)
                data = json.loads(data_raw.decode())
                time = data.get("time")
                print("%s:%s %s:\n%s" % (time[0], time[1], data.get("sender"), data.get("message")))
            except ConnectionResetError:
                print("Connection closed by host")
                break


if __name__ == "__main__":
    client = Client()
