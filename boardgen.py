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

def addRoom(x, y, width, height):
	for i in range(height):
		for j in range(width):
			s = 1 * (i == 0 or j == 0 or i == height - 1 or j == width - 1)
			addBlock(x + j, y + i, s)
	# Add doors
	if random.choices([True, False], weights=[3, 4], k=1)[0]: # Top door
		addBlock(x + random.randint(1, width - 2), y, 2)
	if random.choices([True, False], weights=[3, 4], k=1)[0]: # Bottom door
		addBlock(x + random.randint(1, width - 2), y + height - 1, 2)
	if random.choices([True, False], weights=[3, 4], k=1)[0]: # Left door
		addBlock(x, y + random.randint(1, height - 2), 2)
	if random.choices([True, False], weights=[3, 4], k=1)[0]: # Right door
		addBlock(x + width - 1, y + random.randint(1, height - 2), 2)

extend(y=-1)
addRoom(0, 0, 5, 5)
[addRoom(random.randint(0, 10), random.randint(0, 10), random.randint(5, 10), random.randint(5, 10)) for i in range(5)]

if __name__ == "__main__":
	print("", " " * (boardoffset[0] * 2), end="|")
	for y in range(len(board)):
		print("\n", end=("_" if y == boardoffset[1]-1 else " "))
		for x in range(len(board[y])):
			p = ["-", "X", "~"][board[y][x]]
			print("", p, end="")
	print()
else:
	f = open("board.txt", "w")
	for y in range(len(board)):
		for x in range(len(board[y])):
			f.write(str(board[y][x]))
		f.write("\n")
	f.close()
