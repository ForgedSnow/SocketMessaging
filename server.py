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
        self.sender = name
        self.time = time


class ConnectedUser:
    def __init__(self, id, server, host, port):
        self.id = id
        self.server = server
        self.host = host
        self.port = port
        self.listening = True
        self.thread = Thread(target=self.listening_loop)
        self.thread.start()

    def listening_loop(self):
        #self.send_message(Message("Server", [9, 30, 15, 41000], "Server message"))
        while self.listening:
            try:
                data_raw = self.host.recv(BUFFER_SIZE)
                data = json.loads(data_raw.decode())
            except ConnectionResetError:
                print("client connection error")
                break
            if data.get("type") == "client_message":
                self.server.propagate_message(self.id, data.get("message"))

    def send_message(self, message):
        send_data = json.dumps({"type": 0,
                                "sender": message.sender,
                                "message": message.message,
                                "time": message.time})
        try:
            self.host.send(send_data.encode())
        except Exception:
            print("Message did not send to User %s" % self.id)

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

    def get_time(self):
        time = datetime.datetime.utcnow()
        return time.hour, time.minute, time.second, time.microsecond

    def listening_thread(self):
        open_socket = create_socket()
        open_socket.listen(5)
        while self.accepting_connections:
            with self.print_lock:
                print("Accepting connections....")
            #accept connection
            host, port = open_socket.accept()

            #create connection object, which spawns a new thread
            new_connection = ConnectedUser(self.assign_id(), self, host, port)

            #add new connection object to the list
            self.connection_list.append(new_connection)

            #send join message to everyone
            for connection in self.connection_list:
                message = "User %i has joined the channel" % new_connection.id
                connection.send_message(Message("server", self.get_time(), message))
        #close threads
        for connection in self.connection_list:
            connection.thread.join()

        # close socket
        open_socket.close()

    def propagate_message(self, id, message):
        for connection in self.connection_list:
            connection.send_message(Message(id, self.get_time(), message))

    def assign_id(self):
        with self.id_lock:
            self.connection_id += 1
            return self.connection_id


if __name__ == "__main__":
    server = Instance()
