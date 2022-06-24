import random
import pathfind
from boardgen_lib import *

def addRoom(x, y, width, height):
	for i in range(height):
		for j in range(width):
			isRoomEdge = (i == 0 or j == 0 or i == height - 1 or j == width - 1)
			s = WALL if isRoomEdge else FLOOR
			addBlock(x + j, y + i, s)
	# Add doors
	roomdoors = []
	if random.choices([True, False], weights=[3, 4], k=1)[0]: # Top door
		doorpos = (x + random.randint(1, width - 2), y)
		roomdoors.append(doorpos)
	if random.choices([True, False], weights=[3, 4], k=1)[0]: # Bottom door
		doorpos = (x + random.randint(1, width - 2), y + height - 1)
		roomdoors.append(doorpos)
	if random.choices([True, False], weights=[3, 4], k=1)[0]: # Left door
		doorpos = (x, y + random.randint(1, height - 2))
		roomdoors.append(doorpos)
	if random.choices([True, False], weights=[3, 4], k=1)[0]: # Right door
		doorpos = (x + width - 1, y + random.randint(1, height - 2))
		roomdoors.append(doorpos)
	for doorpos in roomdoors:
		addBlock(doorpos[0], doorpos[1], DOOR)

[addRoom(random.randint(0, 40), random.randint(0, 40), random.randint(5, 10), random.randint(5, 10)) for i in range(10)]
# Add walkways between doors
doorlocs = [(x, y) for x in range(len(board)) for y in range(len(board[0])) if board[x][y] == DOOR]
for doorpos in doorlocs:
	# Find random other door
	otherdoorpos = random.choice([l for l in doorlocs if l != doorpos])
	# Find walkway between doors
	path = pathfind.pathfind(board, doorpos, otherdoorpos, allowedBlocks=[CHASM, DOOR])
	if path == None:
		print("No path found between doors!")
		continue
	print("Yay", end="")
	# Add walkway
	for pos in path:
		if board[pos[0]][pos[1]] not in [CHASM, BOARDWALK]:
			print(".", end="")
		else:
			print("!", end="")
			addBlock(pos[1] - boardoffset[1], pos[0] - boardoffset[0], BOARDWALK)
	print()

if __name__ == "__main__":
	display()
