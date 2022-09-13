import pygame
import random
from math import floor

rooms = []
boardsize = [80, 80]
maxroomsize = 10
minroomsize = 5

def addRoom():
	roomWidth = random.randint(minroomsize, maxroomsize)
	roomHeight = random.randint(minroomsize, maxroomsize)
	roomX = random.randint(0, boardsize[0]) - (roomWidth // 2)
	roomY = random.randint(0, boardsize[1]) - (roomHeight // 2)
	r = pygame.Rect(roomX, roomY, roomWidth, roomHeight)
	if not pygame.Rect(0, 0, boardsize[0], boardsize[1]).contains(r):
		return
	for room in rooms:
		if pygame.Rect(r.left - 1, r.top - 1, r.width + 2, r.height + 2).colliderect(room):
			return
	rooms.append(r)

tries = 0
while len(rooms) < 10 and tries < 100:
	addRoom()
	tries += 1

rooms.sort(key=lambda x: (x.centery, x.centerx))

board = [["wall" for i in range(boardsize[0])] for j in range(boardsize[1])]
for r in rooms:
	for i in range(r.left, r.right):
		for j in range(r.top, r.bottom):
			board[i][j] = "ground"

# Add corridors

def line_range(a, b):
	sign = lambda x: 1 if x >= 0 else -1
	return list(range(a, b, sign(b - a)))

def getCorridor(p1, p2):
	r = []
	if random.randint(0, 1) == 0: # Horizontal first
		for i in line_range(px, nx):
			r.append([i, py]) # Horizontal
		for j in line_range(py, ny):
			r.append([nx, j]) # Vertical
	else: # 						Vertical first
		for j in line_range(py, ny):
			r.append([px, j]) # Vertical
		for i in line_range(px, nx):
			r.append([i, ny]) # Horizontal
	return r

for prev in range(len(rooms) - 1):
	next = prev + 1
	px, py = (floor(rooms[prev].centerx), floor(rooms[prev].centery))
	nx, ny = (floor(rooms[next].centerx), floor(rooms[next].centery))
	for i, j in getCorridor((px, py), (nx, ny)):
		board[i][j] = "ground"
