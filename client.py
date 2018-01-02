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

class GamePlaying():

    def __init__(self, socket, nick):
        self.s = socket
        self.nick = nick
        self.buffer_size = 1024
        self.game = True
        self.l_game = Lock()
        self.state = None
        self.scores = None
        self.board = None
        self.b_update = False
        self.lc_update = Lock()

    def update_state(self, state):
        print "state updated"
        self.state=state

    def update_scores(self, scores):
        print "scores updated"
        self.scores=scores
    def update_board(self):
        self.board.set_board_numbers(self.state)
        self.board.set_table(self.scores)
        self.board.draw_board_numbers()
        self.board.draw_table_score()
    
    def init_board(self):
        self.board = Board(self.nick, self.state, self.scores)# should retur board obj return_board(self.nick, self.state, self.scores)
        
    def update_game(self):
        state = pickle.loads(self.s.recv(buffer_length))
        scores = pickle.loads(self.s.recv(buffer_length))
        print 'update game'
        self.state =  state
        self.scores = scores
        self.update_board()
        #self.board.set_board_numbers(state)
        #self.board.set_table(scores)
        #self.board.draw_board_numbers()
        #self.board.show_board()
        self.s.send(DELIM.join([UPDATE_GAME]) )
        print "Scores"
        print self.scores
        
        #return_board(self.nick, self.state, self.scores)

    def get_status(self):
        with self.l_game:
            status = self.game
        return status
    
    def run(self):
        self.playing = Thread(target=self.playing_game)
        self.listeting = Thread(target=self.listeting_server)
        self.playing.start()
        self.listeting.start()

        #self.playing_game()
    
    def close(self):
        with self.l_game:
            self.game = False
        self.playing.join()
        print "play thread done"
        s.send(DELIM.join([DISCONNECT]))
        self.s.close()
        self.listeting.join(1)
        print "listen thread done"
            

    def playing_game(self):
        prev_turn = (0,(0,0))
        cell = None
        while True:
            with self.l_game:
                status = self.game
            if status == True:
                #cell = self.board.get_last_move()
                #v = self.board.get_val()
                #global lc_cell
                #with lc_cell:
                    #print "accesing g_cell"
                cell = get_gcell()
                time.sleep(2)
                print prev_turn, cell
                if prev_turn!=cell:
                    
                    print self.nick, " playing turn ", cell[1][0], cell[1][1], cell[0]
                   
                    data = DELIM.join([PLAY_TURN,str(cell[1][0]), str(cell[1][1]), str(cell[0])] )
                    self.s.send(data)
                prev_turn = cell
                '''
                if self.b_update == True:
                    with self.lc_update:
                        self.b_update = False
                    self.update_game()
                '''    
            else:
                self.board.end_game()
                break
    

    def listeting_server(self):
        while True:
            with self.l_game:
                status = self.game
            if status == True:
                msg = self.s.recv(self.buffer_size).split(DELIM)
              #  print 'receive from server'
                if msg[0] == GAME_END:
                    with self.l_game:
                        self.game = False
                    print "game ended from server!"

                    winner = self.s.recv(self.buffer_size)

                    print "winner: ", winner
                    break
                if msg[0] == UPDATE_GAME:
                    print "UPDATE REQUEST"
                    #with self.lc_update:
                     #   self.b_update = True
                    self.update_game()
            else:
                break



def stop_execution(signum, taskfrm, game):
    print('You pressed Ctrl+C!')
    game.close()


from functools import partial

def sigint_handler(signum, frame, obj):
    obj.close()

if __name__ == '__main__':

    nick = enter_nickname()

    print "Your nickname: ", nick
    
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
