import random
import time
import select
import struct

from socket import AF_INET, SOCK_STREAM, socket,  SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR,  SO_BROADCAST
from socket import error as soc_err

from threading import Thread, Lock

from xmlrpclib import ServerProxy

from login import *
from sessions_authorization import sessionStart
from Board_gui import Board

from protocol import DELIM
from rpc_session import *

import logging
FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

DEFAULT_SERVER_PORT = 5007
DEFAULT_SERVER_INET_ADDR = '224.0.0.1'
bind_addr = '0.0.0.0'
DEFAULT_RCV_BUFFSIZE = 1024
invited = ''
BD = True
GAME = True


def advertise(s,name, maxp, port):
    ''' Broadcast the game '''
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST,1 ) 
    
    msg = DELIM.join([name, str(maxp), port])
    global BD
    while BD:
        s.sendto(msg, ('<broadcast>',DEFAULT_SERVER_PORT))
        time.sleep(2)

    s.close()

def games_available(s, gamedict, sesslist):
    ''' List of games available '''
    global BD
    s.setblocking(0)
    while BD:
        ready = select.select([s],[],[],2)
        if ready[0]:
            data, addr = s.recvfrom(DEFAULT_RCV_BUFFSIZE)
        else:
            continue
        
        msg = data.split(DELIM)
        if (msg[0],msg[1]) not in sesslist:
            print "server discovered!"
            sesslist.append((msg[0], msg[1]))
            gamedict[msg[0]] = ((addr[0],msg[2]))
            print addr
        
            print "Available games"
        
        time.sleep(2)

def render_board(srv):
    '''Show board in console'''
    cboard = None
    while GAME:
        board = srv.get_sparse()
        if not board == cboard:
            cboard = deepcopy(board)
            print "Game board!"
            print "___________________"
            for i in board:
                print "|".join(str(x) for x in i)
                    
        time.sleep(1)

def render_gui(srv, gui):
    '''Change numbers for GUI'''
    cboard = None
    while GAME:
        board = srv.get_sparse()
        if not board == cboard:
            cboard = deepcopy(board)
            gui.set_board_numbers(cboard)
            gui.draw_board_numbers()
            LOG.info("board updated")
        time.sleep(1)


def run_server(server):
    '''Run RPC srver in client-host'''
    server.serve_forever()
    
    LOG.info("RPC object die")

if __name__ == '__main__':

	#GUI nickname
    nick = enter_nickname()

	#socket for broadcast
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind( ('', DEFAULT_SERVER_PORT ))

	#session GUI, if create new game session - return 'host', if choose existing - 'player', dest - name and size of the session (tuple) 
    inpt, dest = sessionStart(s)
    

    if inpt == "host":     #means that this client is host for this game and start the rpc server
        try:
            s.close()
            game_name = dest[0]
            maxp = int(dest[1])
            
            #Random to check different games on the one computer
            port = "122" + str(random.randint(11,19))

            #Socket broadcast to everyone 
            t = Thread(target=advertise, args = (s, game_name, maxp, port,))
            t.start()
            

            #Socket for waiting players
            msock = socket(AF_INET, SOCK_STREAM)
            msock.bind(("", int(port)))
            msock.listen(maxp)
            
            
            connected = 1
            players = []
            while connected < maxp:
                client, addr = msock.accept()
                LOG.info("Connection from %s:%d", addr[0],addr[1])
                #print "conenction from ", addr, client
                connected +=1
                players.append(client)
                LOG.info("Players %d/%d", connected, maxp)
               # print "players ", connected,"/",maxp
            
            LOG.info("All players conencted! Game start!")
            
            global BD
            BD = False
            t.join()
                       
            for p in players:
                p.send("game started!")

            # Create RPC object
            tservice = RPCService(game_name, maxp)
            server = RPCThreading(("",int(port)+1 ), SimpleXMLRPCRequestHandler) #for working parallel
            server.register_introspection_functions()

            # Register all functions of the Transfer Service
            server.register_instance(tservice)
            
            mt = Thread(target=run_server, args=(server,) )
            mt.start()
            
            if tservice.add_player(nick):
                LOG.info("Player %s added", nick)
        
            while True:
                if tservice.ready():
                    break
                else:
                    time.sleep(0.5)

            LOG.info("All players connected to remote game object!")
            b_init = tservice.get_sparse()
            s_init = tservice.get_scores()
            board = Board(nick, b_init, s_init, tservice)
            
            board.run()
            
            LOG.info("UI closed!")


        except KeyboardInterrupt:
            LOG.info('Ctrl+C issued, terminating ...')
        finally: 
            msock.close()           #Close socket
            LOG.info("Closing socket ...")
            time.sleep(3)
            server.shutdown()       # Stop the serve-forever loop
            server.server_close()   # Close the sockets
            LOG.info('Terminating ...')
            mt.join() 
            exit(0)
    
    if inpt == "player":    #players connected to the host-client
        LOG.info("Connecting to %s:%s", dest[0], dest[1])
        
        msock = socket(AF_INET, SOCK_STREAM)
        msock.connect( (dest[0], int(dest[1])) )

        resp = msock.recv(DEFAULT_RCV_BUFFSIZE)

        LOG.info(resp)
        
        try:
            proxy = ServerProxy("http://%s:%d" % (dest[0], int(dest[1])+1))
            LOG.info('Connected to Mboard XMLRPC server!')

            time.sleep(3)
            
            if proxy.add_player(nick):
                LOG.info("Connection successful")
               
            b_init = proxy.get_sparse()
            s_init = proxy.get_scores()
            board = Board(nick, b_init, s_init, proxy)
            
            board.run()

        except KeyboardInterrupt:
            LOG.warn('Ctrl+C issued, terminating')
            exit(0)
        except Exception as e:
            LOG.error('Communication error %s ' % str(e))
            exit(1)

       

            
            



