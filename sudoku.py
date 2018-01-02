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

import logging as log

DEFAULT_SERVER_PORT = 5007
DEFAULT_SERVER_INET_ADDR = '224.0.0.1'
bind_addr = '0.0.0.0'
DEFAULT_RCV_BUFFSIZE = 1024
invited = ''
BD = True

def advertise(s):
    gamename = "game" + str(random.randint(1,10))
    while BD:
        s.sendto(gamename, ('<broadcast>',DEFAULT_SERVER_PORT))
        time.sleep(2)


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
            
                s = socket(AF_INET, SOCK_DGRAM)
                s.setsockopt(SOL_SOCKET, SO_BROADCAST,1 )
                #s.bind( ('',54545) )
                
                
                t = Thread(target=advertise, args = (s,))
                t.start()
                

                msock = socket(AF_INET, SOCK_STREAM)
                msock.bind(("", 13333))
                msock.listen(1)
                client, addr = msock.accept()
                print "conenction from ", addr
                global BD
                BD = False
                t.join()
                #s.settimeout(0.2)
               # ttl = struct.pack('b', 1)
               # s.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl) 
                   # data, addr = s.recvfrom(DEFAULT_RCV_BUFFSIZE, 2)
                    #if data:
                     #   print "New player ", addr
                      #  print data
                       # break

                break

            if inpt == "s":
                
               # host = "127.0.0." + str(random.randint(1,254))
                port = "2334" + str(random.randint(2,9))
                
                s = socket(AF_INET, SOCK_DGRAM)
                s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                s.bind( ('', DEFAULT_SERVER_PORT ))
                gamelist = []
                while True:
                    data, addr = s.recvfrom(DEFAULT_RCV_BUFFSIZE)

                    if data not in gamelist:
                        print "server discovered!"
                        gamelist.append(data)
                        print addr

                    print "Available games"
                    print gamelist
                    time.sleep(2)
                msock = socket(AF_INET, SOCK_STREAM)
                msock.connect( (addr[0], 13333) )
                #s.sendto("Player1 connected!", (addr[0], 9999) )
                
                
                #membership = inet_aton(DEFAULT_SERVER_INET_ADDR) + inet_aton(bind_addr)
		#s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, membership)
#		s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

 #               s.bind( (bind_addr, DEFAULT_SERVER_PORT) )
  #              data, addr = s.recvfrom(DEFAULT_RCV_BUFFSIZE)

                print "Server discovered!"
                print addr

                break
                


    except KeyboardInterrupt:
        #s.send(DELIM.join([DISCONNECT]))
        s.close()
        msock.close()

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
    print sessions
    s_ret = sessionStart(sessions)
    print 'Size of session', s_ret[1]
    print 'Session name ', s_ret[0]
    
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