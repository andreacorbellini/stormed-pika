import socket
from tornado.iostream import IOStream
import pika.connection

class TornadoConnection(pika.connection.Connection):

    def connect(self, host, port):
        self.socket = socket.socket()
        self.socket.connect((host, port))
        self.io_stream = IOStream(self.socket)
        self.on_connected()
