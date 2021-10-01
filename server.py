import socket
from threading import Thread, Lock, Event
from queue import Queue
import json
import datetime


HOST = ""
PORT = 1212
BUFFER_SIZE = 1024
TIMEOUT = None


class Message:
    def __init__(self, name, time, message):
        self.message = message
        self.name = name
        self.time = time


class ConnectedUser:
    def __init__(self, id, server, host, port):
        self.id = id
        self.server = server
        self.host = host
        self.port = port
        self.connection()

    def connection(self):
        # send user they joined chat message
        time = datetime.datetime.utcnow()
        send_data = json.dumps({"type": 0,
                                "sender": "Server",
                                "message": "User " + str(self.id) + " has successfully joined the channel",
                                "time": [time.hour, time.minute, time.second, time.microsecond]})
        try:
            self.host.send(send_data.encode())
        except Exception:
            print("Client error. Disconnecting")


def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    return s


class Instance:
    def __init__(self):
        self.print_lock = Lock()
        self.id_lock = Lock()
        self.message_lock = Lock()

        self.message_event = Event()

        self.connection_list = []
        self.connection_id = 0

        self.message_list = []

        self.accepting_connections = True
        self.accepting_messages = True
        listening_thread = Thread(target=self.listening_thread)
        listening_thread.start()

    def listening_thread(self):
        open_socket = create_socket()
        open_socket.listen(5)
        while self.accepting_connections:
            with self.print_lock:
                print("Accepting connections....")
            host, port = open_socket.accept()
            temp = Thread(target=ConnectedUser, args=(self.assign_id(), self, host, port))
            self.connection_list.append(temp)
            temp.start()
        #close threads
        for thread in self.connection_list:
            thread.join()
        # close socket
        open_socket.close()

    def assign_id(self):
        with self.id_lock:
            self.connection_id += 1
            return self.connection_id


if __name__ == "__main__":
    server = Instance()
