from datetime import datetime
import socket
from threading import Thread, Lock


class Client(Thread):
    def __init__(self, addr, conn):
        Thread.__init__(self)
        self.host = addr[0]
        self.port = addr[1]
        self.conn = conn

    def run(self):
        """Старт сервера"""
        request = self.conn.recv(DATA_SIZE).decode()
        if request != '':
            webpage = request.split('\n')[0].split()[1]

            if webpage.split('.')[-1] in FILES:
                try:
                    try:
                        with open(FOLDER + webpage, 'r') as f:
                            content = f.read()
                        response = """HTTP/1.1 200 OK
                                Server: WebServer
                                Content-type: text/html
                                Content-length: 7777
                                Connection: close\n\n""" + content
                    except UnicodeDecodeError:
                        with open(FOLDER + webpage, 'rb') as f:
                            content = f.read()
                        response = """HTTP/1.1 200 OK
                                Server: WebServer
                                Content-type: image/png
                                Content-length: 7777
                                Connection: close\n\n"""
                    with lock:
                        with open('log.txt', 'a+') as log:
                            log.write(str(datetime.now()) + ' <---> ' + self.host
                                      + ' <---> ' + webpage + ' <---> None\n')
                except FileNotFoundError:
                    response = 'HTTP/1.0 404 NOT FOUND'
                    with lock:
                        with open('log.txt', 'a+') as log:
                            log.write(str(datetime.now()) + ' <---> ' +
                                      self.host + ' <---> ' + webpage + ' <---> 404\n')
            else:
                if webpage.split('.')[-1] != "ico":
                    response = 'HTTP/1.0 403 FORBIDDEN'
                    with lock:
                        with open('log.txt', 'a+') as log:
                            log.write(str(datetime.now()) + ' <---> ' +
                                      self.host + ' <---> ' + webpage + ' <---> 403\n')

            if "Content-type: image/png" in response:
                self.conn.sendall(response.encode()+content)
            else:
                self.conn.sendall(response.encode())
        self.conn.close()


config = dict()
lock = Lock()
with open('settings.txt', 'r') as f:
    for line in f.readlines():
        k, v = line.split("=")[0], line.split("=")[1]
        config[k] = v

DATA_SIZE = int(config['DATA_SIZE'])
FOLDER = config['DEFAULT_FOLDER'].strip()
FILES = ['html', 'js', 'png', 'jpg', 'jpeg']

sock = socket.socket()
sock.bind((config['DEFAULT_HOST'].strip(), int(config['DEFAULT_PORT'])))
sock.listen(10)


clients = []
while True:
    try:
        conn, addr = sock.accept()
        clients.append(Client(addr, conn))
        clients[-1].start()

        for connect in clients:
            if not connect.is_alive():
                clients.remove(connect)
    except:
        break

sock.close()
