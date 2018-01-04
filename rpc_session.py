import binascii
from Generation import * 
import os
import pickle
from threading import Thread, Lock, Condition
import time
from protocol import *
import operator
import threading
from threading import Thread
import logging
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import SocketServer

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

class RPCThreading(SocketServer.ThreadingMixIn, SimpleXMLRPCServer): pass



# in class server initialize 



class RPCService():  
    def __init__(self, gamename, size):
	'''Service for processing game'''
	self.gamesession = gamename
	self.session_size = size
	self.players = [] # {}
	self.scores = {}
	self.status = False
	question, answer = return_question_and_answer()
        #board
	self.sudoku_full = answer

        #current state
	self.sudoku_sparse = question

        LOG.info("RPC instance created!")
        print "Game answer!"			#Answer for the host to simplify the veryfying checking process
        print "___________________"
	transp_answer = map(list, zip(*answer))
        for i in transp_answer:
            print "|".join(str(x) for x in i)

   
        
    def get_total(self):
        return self.sudoku_full

    def ready(self):
	'''Checking if all players connected'''
        if len(self.players) == self.session_size:
            return True
        else:
            return False

    def get_sparse(self):
        return self.sudoku_sparse

    def get_scores(self):
        return self.scores

    def set_cell(self, cell, value):
        LOG.info("SETTING CELL")
        self.sudoku_sparse[cell[0]][cell[1]] = int(value)
    
    def check_cell(self, cell, value):
        cvalue = self.sudoku_full[cell[0]][cell[1]]
        print cvalue, value
        if int(cvalue) == int(value):
            return True
        else:
            return False

    def game_over(self):
	'''Checking for game ending'''
        if self.sudoku_full == self.sudoku_sparse:
            return True
        else:
            return False


    def add_player(self, name):
	'''Add player to the game'''
	#self.players[name] = socket
        if name not in self.players:
            self.players.append(name)
        else:
            LOG.error("Player name already exist!")
            return False

	self.scores[name] = 0
        return True

    def remove_player(self, name, socket):
	'''Remove player from the game'''
	del self.players[name]
	LOG.info('Player %s disconected', name)

    def get_status(self):
	LoG.info('Is game active? - %s', self.status)
	return self.status

    def play_turn(self, cell, value, name):
	'''Processing the turn of the player'''
	i = int(cell[0])
        j = int(cell[1])
        LOG.info('Player {} put in cell ({}, {}): value {}'.format(name, i, j, value))
	#checking winning condition
	board_ans = self.get_total()
	LOG.info('matrix = {} ({}, {})'.format(board_ans[i][j], i, j))
	LOG.info('value = {}'.format(value))
	LOG.info('Checking cell...')
        
        if self.sudoku_sparse[cell[0]][cell[1]] > 0:
            return not self.game_over()
        
        if self.check_cell(cell, value):
            LOG.info("UPD BOARD & SCORES")
            self.scores[name] += 1
            self.set_cell(cell, value)
        else: 
            self.scores[name] -= 1

        LOG.info('Turn played')

        return not self.game_over()




	
	

