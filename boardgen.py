import random

board = [[0 for y in range(1)] for x in range(1)]
boardoffset = [0, 0]

def extend(x = 0, y = 0):
	if x < 0:
		# Add rows to the left
		for i in range(abs(x)):
			board.insert(0, [0 for y in range(len(board[0]))])
		# Update the offset
		boardoffset[0] -= x
	elif x > 0:
		# Add rows to the right
		for i in range(x):
			board.append([0 for y in range(len(board[0]))])
	if y < 0:
		# Add columns to the top
		for i in range(abs(y)):
			for row in board:
				row.insert(0, 0)
		# Update the offset
		boardoffset[1] -= y
	elif y > 0:
		# Add columns to the bottom
		for i in range(y):
			for row in board:
				row.append(0)

def addBlock(x, y, state):
	boardpos = [y + boardoffset[1], x + boardoffset[0]]
	# Extend board if boardpos doesn't exist
	if boardpos[1] < 0: # To the top
		extend(x=boardpos[1])
		boardpos = [y + boardoffset[1], x + boardoffset[0]]
	if boardpos[1] >= len(board[0]): # To the right
		extend(y=boardpos[1] - len(board[0]) + 1)
		boardpos = [y + boardoffset[1], x + boardoffset[0]]
	if boardpos[0] < 0: # To the left
		extend(y=boardpos[0])
		boardpos = [y + boardoffset[1], x + boardoffset[0]]
	if boardpos[0] >= len(board): # To the bottom
		extend(x=boardpos[0] - len(board) + 1)
		boardpos = [y + boardoffset[1], x + boardoffset[0]]
	# Place block
	board[boardpos[0]][boardpos[1]] = state

extend(y=-1)
addBlock(-1, 1, 1)
print("", " " * (boardoffset[0] * 2), end="|")
for y in range(len(board)):
	print("\n", end=("_" if y == boardoffset[1]-1 else " "))
	for x in range(len(board[y])):
		print("", board[y][x], end="")
print()
