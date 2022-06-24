import random
import pathfind
from boardgen_lib import *

def addRoom(x, y, width, height):
	for i in range(height):
		for j in range(width):
			isRoomEdge = (i == 0 or j == 0 or i == height - 1 or j == width - 1)
			s = WALL if isRoomEdge else FLOOR
			addBlock(x + j, y + i, s)

def addCenteredRoom(x, y):
	w = random.randint(5, 10)
	h = random.randint(5, 10)
	addRoom(x - (w // 2), y - (h // 2), w, h)

points = [(random.randint(0, 40), random.randint(0, 40)) for i in range(10)]
[addCenteredRoom(*point) for point in points]

# Add walkways
for begin in points:
	end = random.choice([p for p in points if p != begin])
	path = pathfind.pathfind(board, begin, end, allowedBlocks={CHASM: 1, WALL: 4, FLOOR: 3})
	if path:
		print("Path found")
		for point in path:
			if getBlock(point[0], point[1]) == CHASM:
				# Make sure there are not too many boardwalks in the area
				d = 0
				if getBlock(point[0] - 1, point[1]) == BOARDWALK: d += 1
				if getBlock(point[0] + 1, point[1]) == BOARDWALK: d += 1
				if getBlock(point[0], point[1] - 1) == BOARDWALK: d += 1
				if getBlock(point[0], point[1] + 1) == BOARDWALK: d += 1
				# Add the boardwalk
				if d < 3: addBlock(point[0], point[1], BOARDWALK)
			elif getBlock(point[0], point[1]) == WALL:
				# Make sure there are not two doors next to each other
				if getBlock(point[0] - 1, point[1]) == DOOR: continue
				if getBlock(point[0] + 1, point[1]) == DOOR: continue
				if getBlock(point[0], point[1] - 1) == DOOR: continue
				if getBlock(point[0], point[1] + 1) == DOOR: continue
				# Make sure there are not too many walls in the area
				d = 0
				if getBlock(point[0] - 1, point[1]) == BOARDWALK: d += 1
				if getBlock(point[0] + 1, point[1]) == BOARDWALK: d += 1
				if getBlock(point[0], point[1] - 1) == BOARDWALK: d += 1
				if getBlock(point[0], point[1] + 1) == BOARDWALK: d += 1
				# Add door
				if d < 3: addBlock(point[0], point[1], DOOR)
	else:
		print("No path found from", begin, "to", end)

if __name__ == "__main__":
	display()
