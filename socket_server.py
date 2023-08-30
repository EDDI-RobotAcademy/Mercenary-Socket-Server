import socket as sk
import multiprocessing as mp
from datetime import datetime as dt
import logging

class SocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.logger = self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.DEBUG)
        return logging.getLogger(__name__)

    def handler(self, conn, address):
        with conn:
            data = conn.recv(1024)
            command_str = data.decode().strip()
            self.logger.debug('{} command received [{}] from {}'.format(dt.now(), command_str, address[0]))
            if len(data) > 0:
                resp = 'server: {} message received [{}] from {}'.format(dt.now(), command_str, address[0])
                conn.sendall(resp.encode())
                return

    def start(self):
        self.logger.debug('server started {}'.format(dt.now()))
        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as self.server_socket:
            try:
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(1)
                while True:
                    conn, address = self.server_socket.accept()
                    with conn:
                        self.logger.debug('{} received data from {}'.format(dt.now(), address[0]))
                        p = mp.Process(target=self.handler, args=(conn, address))
                        p.daemon = True
                        p.start()
                        self.logger.debug('{} created process {}'.format(dt.now(), p.pid))

            except Exception as e:
                self.logger.debug(e)
                self.kill_all_process()
            except KeyboardInterrupt:
                self.logger.debug('server stopped')
                self.kill_all_process()
            finally:
                self.kill_all_process()

    def kill_all_process(self):
        for p in mp.active_children():
            self.logger.debug('pid : {} terminated'.format(p.pid))
            p.terminate()
            p.join()

if __name__ == '__main__':
    server = SocketServer('0.0.0.0', 33333)
    server.start()