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
	self.gamesession = gamename
	self.session_size = size
	self.players = {}
	self.scores = {}
	self.status = False
	question, answer = return_question_and_answer()
        #board
	self.sudoku_full = answer

        #current state
	self.sudoku_sparse = question

        LOG.info("RPC instance created!")

    def get_total(self):
        return self.sudoku_full

    def set_cell(self, cell, value):
        self.sudoku_sparse[cell[0]][cell[1]] = value
    
    def check_cell(self, cell, value):
        cvalue = self.sudoku_full[cell[0]][cell[1]]
        print cvalue, value
        if cvalue == value:
            return True
        else:
            return False

    def game_over(self):
        if self.sudoku_full == self.sudoku_sparse:
            return True
        else:
            return False


    def add_player(self, name, socket):
	self.players[name] = socket
	self.scores[name] = 0

    def remove_player(self, name, socket):
	del self.players[name]
	LOG.info('Player %s disconected', name)

    def get_status(self):
	LoG.info('Is game active? - %s', self.status)
	return self.status

    def play_turn(self, cell, value, name):
	i = int(cell[0])
        j = int(cell[1])
        LOG.info('Player {} put in cell ({}, {}): value {}'.format(name, i, j, value))
	#checking winning condition
	board_ans = self.get_total()
	LOG.info('matrix = {} ({}, {})'.format(board_ans[i][j], i, j))
	LOG.info('value = {}'.format(value))
	LOG.info('Checking cell...')
	if board_ans == value:
            self.scores[name] += 1
                    #self.session.set_cell(cell, value)
        else: 
            self.scores[name] -= 1

        LOG.info('Turn played')


    def update_clients_scores(self):
        LOG.info('Update........score')

    def update_game(self):
        LOG.info('Update......game')


	
	
