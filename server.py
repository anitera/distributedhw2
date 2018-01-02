from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR
from argparse import ArgumentParser
from client_handler import ClientHandler
from sessions import load_sessions, save_sessions, current_sessions, cv_session
from threading import Thread, Condition
# Constants
buffer_length = 1024




class Server():
    
    def listen(self, sock_addr, backlog = 1):
        self.__sock_addr = sock_addr
        self.__backlog = backlog
        self.__s = socket(AF_INET, SOCK_STREAM)
        self.__s.bind(self.__sock_addr)
        self.__s.listen(self.__backlog)
        self.sess_names = [] #load_sessions()
      #  self.cv_sess = Condition()
        sess_thread = Thread(target=self.session_updater)
        sess_thread.start()
        print "Socket %s:%d is in listning state" % ( self.__s.getsockname() )

    def start(self):
        clients = []
        try:
            while True:
                client_socket = None
                print "waiting clients..."
                client_socket, client_addr = self.__s.accept()
                c = ClientHandler(client_socket, client_addr)
                c.set_sessions(self.sess_names)
                clients.append(c)
                c.start()
        except KeyboardInterrupt:
            print "Ctrl+C"
            self.__s.close()
        finally:
            if client_socket != None:
                client_socket.close()
            self.__s.close()
        self.__s.close()
        map(lambda x: x.join(), clients)
    
    def session_updater(self):
        with cv_session:
            while True:
                self.sess_names = current_sessions()
                print "Current sessions"
                print self.sess_names
                cv_session.wait()

if __name__ == '__main__':

    s = Server()
    s.listen( ('127.0.0.49', 7777 ) )
    s.start()
    '''
    parser = ArgumentParser()
    parser.add_argument('-H','--Host',\
                        help='host',\
                        required=False,\
                        default='127.0.0.1')
    parser.add_argument('-p','--port',\
                        help='port',\
                        required=False,\
                        default=7777)
    args = parser.parse_args()
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((args.Host, args.port))

    backlog = 0 # Waiting queue size, 0 means no queue
    s.listen(backlog)

    while True:
            try:
	        client_socket,client_addr = s.accept()
            except socket.error, exc:
                print 'Caught socket exceptopn', exc
            try:
	        nickname = client_socket.recv(buffer_length)
            except socket.error:
                print 'Socket error'
            if validate_nickname(nickname):
                client_socket.send('1')
            else:
                client_socket.send('0')
	    client_socket.close()
    s.close()
    '''
