import binascii
from Generation import * 
import os
import pickle
from threading import Thread, Lock, Condition
import time
from protocol import *
import operator
# Constants -------------------------------------------------------------------
___NAME = 'Sessions Protocol'
___VER = '0.0.0.1'
___DESC = 'Simple Sessions protocol (server-side)'
___BUILT = '2016-08-23'
___VENDOR = 'Copyright (c) 2016 DSLab'
# Private variables -----------------------------------------------------------
M = [] # Received messages (array of tuples like ( ( ip, port), data)
S = {} # Sessions
GH = {}
OUTBOX = {}
INBOX = {}
sess_id_counter = 0
cv_session = Condition()
lc_message = Lock()
#from server import cv_session

#return_question_and_answer question (blank),answer (filled)
#
def get_name(token):
   
    print "get name by token ", token
    return GH[token].get_name()

def add_player(token, nick, socket):
    GH[token].add_player(nick, socket)

def remove_player(token, nick, socket):
    GH[token].remove_player(nick, socket)

class Player():
    def __init__(self, name, socket):
        self.name = name
        self.socket = socket

    def get_name(self):
        return self.name

    def get_socket(self):
        return self.socket

    def send(self, data):
        try:
            self.socket.send(data)
            return True
        except:
            print "cannot send data to player ", self.name
            return False


class GameHandler(Thread):

    def __init__(self, GameSession):
        Thread.__init__(self)
        self.session = GameSession
        self.players = {}
        self.scores = {}
        #self.lock_layers = Lock()
        self.cv_players = Condition()
        self.cv_turn = Condition()

        self.game = False
        self.m_game = Lock()
        self.m_update = Lock()
        self.lc_sess = Lock()
        #self.lock = Lock()
        print "Game Session ", self.session.name, " started!"

    def add_player(self, name, socket):
        with self.cv_players:
            self.players[name] =  socket
            self.scores[name] = 0
            self.cv_players.notify()


    def remove_player(self, name, socket):
        with self.cv_players:
            del self.players[name]
            print "player ", name, " disconected"
            self.cv_players.notify()

    def get_token(self):
        tkn = None
        with self.lc_sess:
            tkn = self.session.get_token()
        return tkn
     
    def get_name(self):
        name = ""
        with self.lc_sess:
            name = self.session.get_name()
        return name

    def get_status(self):
        with self.m_game:
            status = self.game
        return status

    def play_turn(self, cell, value, name):
        with self.cv_turn:
            print "player ", name, " place ", value, " in cell ", cell
            i = int(cell[0])
            j = int(cell[1])
            #check if cell is equal board_ans = session.get_total()
            board_ans = None
            with self.lc_sess:
                board_ans = self.session.get_total()
            print 'matrix=',board_ans[i][j], '(', i, ',', j,')'
            print 'value=', value
	    with self.m_update:
                print "checking cell..."
                #act =  None
                #with self.lc_sess:
                 #   act = self.session.check_cell(cell,value)
                if board_ans == value:
                    self.scores[name] += 1
                    #self.session.set_cell(cell, value)
                else: 
                    self.scores[name] -= 1
            print "turn played"
            self.cv_turn.notify()
    def game_over(self):
        st = None
        with self.lc_sess:
            st = self.session.game_over()
        return st

    def send_to_players(self, data):
        for k, v in self.players.items():
            v.send(data)


    def update_clients_boards(self):
        with self.m_update:
            state = None
            with self.lc_sess:
                state = self.session.get_state()
            #print "sending state"
           # print state
            for k, v in self.players.items():
               # print "sending for player ", k
                v.send(pickle.dumps(state, -1) )

    def update_clients_scores(self):
        with self.m_update:
            scores = self.scores
            print "sending scores"
            print scores
            for k,v in self.players.items():
                print "sending for player ", k
                v.send(pickle.dumps(scores, -1) )

    def update_game(self):
        print "updating game"
        with lc_message:
            buff = 1024
            for k,v in self.players.items():
                print "send ", k, " updating request"
                v.send(UPDATE_GAME)
        time.sleep(1)    
        self.update_clients_boards()
        self.update_clients_scores()

    def run(self):
        
        with self.cv_players:
            while True:    
                if not len(self.players) == self.session.size:
                    print "waiting players ", len(self.players), "/", self.session.size 
                else:
                    print "Enough players! Staring game..."
                    with self.m_game:
                        self.game = True
                    break
                self.cv_players.wait()
        
        
        self.observer = Thread(target=self.game_observer )
        self.observer.start()
        
        self.update_game()
       
        with self.cv_turn:
            while True:
                with self.m_game:
                    status = self.game
                if status == True:
                    self.cv_turn.wait()
                    print "checking game state..."
                    self.update_game()

                    if self.game_over() == True:
                        break
        
                else:
                    print "game done!"
                    break
        
        self.send_to_players(GAME_END)
        winner = ""
        if len(self.players) > 0:
            winner = max(self.players.iteritems(), key=operator.itemgetter(1))[0]
        else:
            winner = self.players.keys()
        
        
        print "Player ", winner, " win!"

        self.send_to_players(winner)

        print "Game session ", self.get_name()," closed!"

    def game_observer(self):
        while True:
            with self.cv_players:
                print "players remain ", len(self.players)
                if len(self.players) == 1:
                    with self.cv_turn:
                        with self.m_game:
                            self.game = False
                        self.cv_turn.notify()
                    break
                self.cv_players.wait()
        print "no players left"

class GameSession():

    def __init__(self, session_size):
	'''Creating new session with specified size
        @param session_size: max number of players in session
        '''
	global sess_id_counter
	self.size = session_size
        #generate session token
	self.token = binascii.hexlify(os.urandom(16))
	sess_id_counter += 1
	self.id = sess_id_counter
        # call function from Generation.py
	question, answer = return_question_and_answer()

        #board
	self.sudoku_full = answer

        #current state
	self.state = question

        #session name
        self.name = {}

    def get_token(self):
        return self.token

    def get_size(self):
        return self.size

    def get_state(self):
        return self.state

    def get_total(self):
        return self.sudoku_full

    def set_name(self, name):
        self.name = name
    
    def get_name(self):
        return self.name

    def set_cell(self, cell, value):
        self.state[cell[0]][cell[1]] = value
    
    def check_cell(self, cell, value):
        cvalue = self.sudoku_full[cell[0]][cell[1]]
        print cvalue, value
        if cvalue == value:
            return True
        else:
            return False

    def game_over(self):
        if self.sudoku_full == self.state:
            return True
        else:
            return False

def new_session(source, session_size, name):
    '''Create new session, give it unique iD
    @param source: tuple ( ip, port ), socket address of the session originator
    @param session_size: max number of players in session
    @returns hex, session token
    '''
    global S, GH, cv_session
    with cv_session:
        sess = GameSession(session_size)
        token = sess.get_token()
        sess.set_name(name)
        S[token] = sess
        GH[token] = GameHandler(sess)
        GH[token].start()
        cv_session.notify()

    
    #print "Sess token ", token
    return GH[token]

def get_session(name):
   
    print "get session ", name
    for k, v in GH.items():
        if v.get_name() == name:
            return GH[k]
    
def save_sessions(cv):
    with cv:
        global S
        with open("sessions.bin", 'wb') as f:
            pickle.dump(S, f, pickle.HIGHEST_PROTOCOL)
    
    cv.notify()


def current_sessions():
    sess_names = [ (v.session.get_size(), v.get_name()) for k,v in GH.iteritems() ] 
    return sess_names

def load_sessions():
    global S
    try:
        with open('sessions.bin', 'rb') as handle:
            S = pickle.load(handle)
        if len(S) > 0:
            print len(S), " session loaded!"
            print S
            sess_names = [ x.name for x in S.values() ]
            return sess_names
        else:
            return []
            print "No loaded sessions!"
    except:
        print "No session dump!"
        return []
