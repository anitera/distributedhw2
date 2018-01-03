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

    '''
    s = socket(AF_INET, SOCK_STREAM)

    while True:
        #inpt = raw_input("Enter dedicated host address [ip:port]: ")
        HP = HostPort()
        hostPortAuthorization(HP)
        host, port = HP.getHostPort()
        if port.isdigit():
            port = int(port)
            if s.connect_ex( (host, port) ) != 0:
                print "Incorrect host address. Try again!"
            else:
                print "Connection established!"
                break
    ''' 
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
                
                time.sleep(3)

                board = Thread(target=render_board, args=(tservice,) )
                board.start()
                
                if tservice.add_player(nick):
                    LOG.info("Player %s added", nick)

             

                
                
                '''
                v = int(raw_input("value:"))
                i = int(raw_input("i:"))
                j = int(raw_input("j:"))

                tt = tservice.play_turn((i,j),v,nick)

                while tt:
                    v = int(raw_input("value:"))
                    i = int(raw_input("i:"))
                    j = int(raw_input("j:"))

                    tt = tservice.play_turn((i,j),v,nick)
                    print tt
                    time.sleep(1)

                board.join()
                '''
                mt.join()
                       
        
            if inpt == "s":
                
               # host = "127.0.0." + str(random.randint(1,254))

                
                s = socket(AF_INET, SOCK_DGRAM)
                s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                s.bind( ('', DEFAULT_SERVER_PORT ))
                gamedict = {}
                sesslist = []
                
                t = Thread(target = games_available, args=(s, gamedict, sesslist,))
                t.start()

                k = int(raw_input("Session #:")) #random.randint(0, len(gamelist))
                s_ret = sessionStart(sesslist)
                print 'Size of session', s_ret[0]
                print 'Session name ', s_ret[1]

                dest = gamedict[s_ret[1]]

                msock = socket(AF_INET, SOCK_STREAM)
                msock.connect( (dest[0], int(dest[1])) )

                resp = msock.recv(DEFAULT_RCV_BUFFSIZE)

                print resp

                global BD
                BD = False
                t.join()


                try:
        	    proxy = ServerProxy("http://%s:%d" % (dest[0], int(dest[1])+1))
    		except KeyboardInterrupt:
        	    LOG.warn('Ctrl+C issued, terminating')
        	    exit(0)
    		except Exception as e:
        	    LOG.error('Communication error %s ' % str(e))
        	    exit(1)

		LOG.info('Connected to Mboard XMLRPC server!')

                gg = proxy.add_player(nick)
                #    LOG.info("Player %s added", nick)
                
                time.sleep(3)
                
                b_init = proxy.get_sparse()
                s_init = proxy.get_scores()
                board = Board(nick, b_init, s_init)
                #board.draw_board_numbers()
                #board.draw_table_score()
                render_gui = Thread(target = render_gui, args=(proxy, board,))
                render_gui.start()

                while True:
                   # board.draw_board_numbers()
                    #board.draw_table_score()
                    board.frame.mainloop()
                    cell = board.get_last_move()
                    v = cell[0]
                    pos = cell[1]

                    tt = proxy.play_turn(pos, v, nick)

                render_gui.join()

                '''
                board = Thread(target=render_board, args=(proxy,) )
                board.start()


                v = int(raw_input("value:"))
                i = int(raw_input("i:"))
                j = int(raw_input("j:"))

                tt = proxy.play_turn((i,j),v,nick)

                while tt:
                    v = int(raw_input("value:"))
                    i = int(raw_input("i:"))
                    j = int(raw_input("j:"))

                    tt = proxy.play_turn((i,j),v,nick)
                    print tt
                    time.sleep(1)

                #s.sendto("Player1 connected!", (addr[0], 9999) )
                
                
                #membership = inet_aton(DEFAULT_SERVER_INET_ADDR) + inet_aton(bind_addr)
		#s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, membership)
#		s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

 #               s.bind( (bind_addr, DEFAULT_SERVER_PORT) )
  #              data, addr = s.recvfrom(DEFAULT_RCV_BUFFSIZE)
                '''
                break
                


    except KeyboardInterrupt:
        #s.send(DELIM.join([DISCONNECT]))
        s.close()
        msock.close()
        LOG.info('Ctrl+C issued, terminating ...')
    
        server.shutdown()       # Stop the serve-forever loop
        server.server_close()   # Close the sockets
        LOG.info('Terminating ...')


        #HP = HostPort()
        #hostPortAuthorization(HP)
        #host, port = HP.getHostPort()
        #if port.isdigit():
    #        port = int(port)
     #       if s.connect_ex( (host, port) ) != 0:
      #          print "Incorrect host address. Try again!"
       #     else:
        #        print "Connection established!"
         #       break

    #sessionStart() # session start window

    print "Multiplayer Game"
    flag_of_new_session = True

    sessions  = pickle.loads(s.recv(buffer_length))
      
    for sess in sessions:
        if s_ret[0] == sess[1]:
            flag_of_new_session = False



    # here we need to know id of our session and max number of clients
    #current_session = ""
    #if len(sessions) > 0:
    #    print "Current session"
    #    for ss in sessions:
    #        print ss

    #    sess_name = raw_input("choose sess name or 0 to procceed: ")
    #    if sess_name == "0":
    #        print "create a new sesson"
    #        flag_of_new_session = True
    #    else:
    #        snames = [x[1] for x in sessions ] 
    #        if sess_name in snames:
    #            current_session = sess_name
    #        else:
    #            print "Session doesnt exist"
    #else:
    #    flag_of_new_session = True

    #session_id = 0
    # session_size = 4

    if flag_of_new_session:
        
        s.send(DELIM.join([NEW_SESSION, s_ret[0], str(s_ret[1]), nick]))
	
    else: 
        print "Session=", s_ret[0], " Nick=", nick
        s.send(DELIM.join([OLD_SESSION, s_ret[0], nick]))
	#s.send('1' + ' ' + nick + ' ' + str(session_id))
 

    '''getting session token, save it in client side and always send message with it
    because server should recognize for which session data incoming
    '''
    try:
        sess = s.recv(buffer_length)
        print "Session token ", sess
    except:
        print "socket errot"

    '''
    rspn = s.recv(buffer_length)
    
    if rspn == GAME_START:
        print "session started"
        s.send(OK)
    else:
        print "session error"
    '''

    rspn = s.recv(buffer_length)
    board = None
    scores = None
    if rspn == UPDATE_GAME:
        
        board = pickle.loads(s.recv(buffer_length) )

        print "BOARD FOR GAME"
        print board

        scores = pickle.loads(s.recv(buffer_length) )

        print "SCORES"
        print scores
        s.send(DELIM.join([UPDATE_GAME]))
    else:
        print "wrong request"
        print rspn

    game = GamePlaying(s, nick)
    game.update_state(board)
    game.update_scores(scores)
    game.init_board()
    time.sleep(random.randint(10,20))
    
    game.run()
    game.update_board()
    game.board.frame.mainloop()
    #game.playing_game()
    
    '''
    while True:
        exit = int(raw_input("exit?"))
        if exit == 1:
            game.close()
            break
        elif game.get_status() == False:
            game.close()
            break
    print "Thank you for playing!" 
    '''
    '''
    try:
        while True:
            print "playing.."
            time.sleep(10)
            cell = list([random.randint(1,9), random.randint(1,9)])
            value = random.randint(1,9)
            data = DELIM.join([PLAY_TURN,str(cell[0]), str(cell[1]), str(value)] )
            s.send(data)
    except KeyboardInterrupt:
        s.send(DELIM.join([DISCONNECT]))
        s.close()
    '''
    # get current players and their score from session with dictionary table_score = { 'nickname': score}
  #  table_score = {'olha': 0, 'slava': 0, 'rita': 0, 'vasya': 0}

#    return_board(nick, host, port, session_id, session_size, table_score)



    '''
    s = socket(AF_INET, SOCK_STREAM)

    server_address = (args.Host, int(args.port))

    s.connect(server_address)
    try:
        s.send(args.nickname)
    except socket.error:
        #print 'Socket error'
    try:
        message = s.recv(buffer_length) 
    except socket.error:
        print 'Socket error'
    print message

    if message == "1":
        print ""
    '''
    #s.close()
