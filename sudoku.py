from socket import AF_INET, SOCK_STREAM, socket
from argparse import ArgumentParser
import curses
import os
from login import *
from host_port_authorization import *
from sessions_authorization import *
from Board_gui import *
import time
buffer_length = 5024
from xmlrpclib import ServerProxy

from protocol import *
import pickle
import random
from threading import Thread, Lock
import signal
from Board_gui import *
from threading import Thread
from argparse import ArgumentParser
import socket
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SOL_IP, SOCK_STREAM, SO_BROADCAST
from socket import IPPROTO_IP, IP_MULTICAST_LOOP, IP_MULTICAST_TTL, INADDR_ANY, IPPROTO_UDP
from socket import inet_aton, IP_ADD_MEMBERSHIP, socket
from socket import error as soc_err
import struct
import sys
import thread
from rpc_session import *
import select
from copy import deepcopy
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
    msg = DELIM.join([name, str(maxp), port])
    global BD
    while BD:
        s.sendto(msg, ('<broadcast>',DEFAULT_SERVER_PORT))
        time.sleep(2)

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

    server.serve_forever()


if __name__ == '__main__':

    nick = enter_nickname()

    print "Your nickname: ", nick

    try:
        while True:
            inpt = raw_input("Host \ search (h \ s): ")
            if inpt == "h":
                name = raw_input("Game name:")
                maxp = int(raw_input("Num players:"))

		#Socket broadcast to everyone
                s = socket(AF_INET, SOCK_DGRAM)
                s.setsockopt(SOL_SOCKET, SO_BROADCAST,1 )
                #s.bind( ('',54545) )
                
                #Random to ckeck different games on the one computer
                port = "122" + str(random.randint(11,19))
                t = Thread(target=advertise, args = (s,name, maxp, port,))
                t.start()
                

		#Socket for waiting players
                msock = socket(AF_INET, SOCK_STREAM)
                msock.bind(("", int(port)))
                msock.listen(maxp)
                connected = 1
                players = []
                while connected < maxp:
                    client, addr = msock.accept()

                    print "conenction from ", addr, client
                    connected +=1
                    players.append(client)
                    print "players ", connected,"/",maxp
                
                print "All players conencted! Game start!"
                global BD
                BD = False
                t.join()
                s.close()
                
                for ss in players:
                    ss.send("game started!")

		# Create RPC object
                tservice = RPCService(name, maxp)
                server = RPCThreading(("",int(port)+1 ), SimpleXMLRPCRequestHandler) #for working parallel
                server.register_introspection_functions()

                # Register all functions of the Transfer Service
                server.register_instance(tservice)
                
                mt = Thread(target=run_server, args=(server,) )
                mt.start()
                

#                board = Thread(target=render_board, args=(tservice,) )
 #               board.start()
                
                if tservice.add_player(nick):
                    LOG.info("Player %s added", nick)

             

                while True:
                    if tservice.ready():
                        break
                    else:
                        time.sleep(0.5)
                        LOG.info("checkready")
  
                LOG.info("All players connected!")
                b_init = tservice.get_sparse()
                s_init = tservice.get_scores()
                board = Board(nick, b_init, s_init, tservice)
                #while True:
                board.run()
                 
                server.shutdown()       # Stop the serve-forever loop
                server.server_close()   # Close the sockets
                LOG.info('Terminating ...')
                mt.join()

                break
                       
        
            if inpt == "s":
                
               # host = "127.0.0." + str(random.randint(1,254))

                
                s = socket(AF_INET, SOCK_DGRAM)
                s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                s.bind( ('', DEFAULT_SERVER_PORT ))
                gamedict = {}
                sesslist = []
                
               # t = Thread(target = games_available, args=(s, gamedict, sesslist,))
                #t.start()

                #k = int(raw_input("Session #:")) #random.randint(0, len(gamelist))
                dest = sessionStart(sesslist, s)
                print 'Port', dest[1]
                print 'Host ', dest[0]

               # dest = gamedict[s_ret[1]]

                msock = socket(AF_INET, SOCK_STREAM)
                msock.connect( (dest[0], int(dest[1])) )

                resp = msock.recv(DEFAULT_RCV_BUFFSIZE)

                print resp

                global BD
                BD = False
                
                try:
        	    proxy = ServerProxy("http://%s:%d" % (dest[0], int(dest[1])+1))
    		except KeyboardInterrupt:
        	    LOG.warn('Ctrl+C issued, terminating')
        	    exit(0)
    		except Exception as e:
        	    LOG.error('Communication error %s ' % str(e))
        	    exit(1)

		LOG.info('Connected to Mboard XMLRPC server!')

                time.sleep(3)


                gg = proxy.add_player(nick)
                #    LOG.info("Player %s added", nick)
                
                b_init = proxy.get_sparse()
                s_init = proxy.get_scores()
                board = Board(nick, b_init, s_init, proxy)
                #while True:
                board.run()

                break
                


    except KeyboardInterrupt:
        #s.send(DELIM.join([DISCONNECT]))
        s.close()
        msock.close()
        LOG.info('Ctrl+C issued, terminating ...')
    
        server.shutdown()       # Stop the serve-forever loop
        server.server_close()   # Close the sockets
        LOG.info('Terminating ...')
