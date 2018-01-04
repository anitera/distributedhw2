import random
import sudoku_solver

class Scale(object):
	''' A class that will generate the game '''
	size = property(lambda self: self.__size)

	def __init__(self, size = 3):		
		self.__size = size
		self.board = []
		for i in xrange (size**2):
			self.line = []
			for j in xrange (size**2):
				self.line.append((i*size + i//size + j) % (size**2) + 1)
			self.board.append(self.line)

	def show(self):
		''' show the board '''	
		for i in xrange(self.size**2):
			print self.board[i]

	def transp(self):
		''' Transposition of the board	 '''
		self.board = map(list, zip(*self.board))

	def rows_change(self):
		''' set rows for the game '''
		square = random.randrange(self.size)
		line = random.randrange(self.size)
		number = square*self.size + line
		second_line = random.randrange(self.size)
		while line == second_line:
			second_line = random.randrange(self.size)
		second_number = square*self.size + second_line
		temp = self.board[number]
		self.board[number] = self.board[second_number]
		self.board[second_number] = temp

	def colums_change(self):
		''' set columns for the game '''
		Scale.transp(self)
		Scale.rows_change(self)
		Scale.transp(self)	

	def square_change_horizontal(self):
		''' set numbers horizontally in sudoku '''
		square = random.randrange(self.size)
		second_square = random.randrange(self.size)
		while square == second_square:
			second_square = random.randrange(self.size)
		for i in xrange (0, self.size):
			number = square*self.size + i
			second_number = second_square*self.size + i
			temp = self.board[number]
			self.board[number] = self.board[second_number]
			self.board[second_number] = temp

	def square_change_vertical(self):
		''' set numbers vertically in sudoku '''
		Scale.transp(self)
		Scale.square_change_horizontal(self)
		Scale.transp(self)

	def combination(self, shuffle = 15):
		''' shuffle whole table '''
		shuffle_variants = (self.transp, self.rows_change, self.colums_change, self.square_change_horizontal, self.square_change_vertical)
		for i in xrange(shuffle):
			random.choice(shuffle_variants)()	

def return_answer():
	''' return the answer '''
	sc = Scale(3)
	sc.combination(20)
	return sc

def return_question_and_answer():
	''' return question and the answer '''
	
	answer = return_answer()
	size = answer.size
	question = []
	for i in xrange (size**2):
			line = []
			for j in xrange (size**2):
				line.append(answer.board[i][j])
			question.append(line)
	visited = []
	for i in xrange (size**2):
		visited.append([0] * size**2)	
	counter = 0

	while counter < size**4:
		i = random.randrange(size**2)
		j = random.randrange(size**2)
		if visited[i][j] == 0:
			counter  += 1
			visited[i][j] = 1
			temp = question[i][j]
			question[i][j] = 0
			solution = []
			for k in xrange (size**2):
				solution.append(question[k][:])
			solve = 0
			for s in sudoku_solver.solve_sudoku((size, size), solution):
				solve += 1
			if solve != 1:
				question[i][j] = temp
		
	return question, answer.board
