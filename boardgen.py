import pygame
import random
from math import floor

rooms = []

def addRoom():
	r = pygame.Rect(random.randint(0, 50), random.randint(0, 50), random.randint(5, 10), random.randint(5, 10))
	for room in rooms:
		if pygame.Rect(r.left - 1, r.top - 1, r.width + 2, r.height + 2).colliderect(room):
			return
	rooms.append(r)

tries = 0
while len(rooms) < 10 and tries < 100:
	addRoom()
	tries += 1

rooms.sort(key=lambda x: (x.centery, x.centerx))

board = [["air" for i in range(60)] for j in range(60)]
for r in rooms:
	for i in range(r.left, r.right):
		for j in range(r.top, r.bottom):
			board[i][j] = "stuff"

# Add corridors

def line_range(a, b):
	sign = lambda x: 1 if x >= 0 else -1
	return list(range(a, b, sign(b - a)))

for prev in range(len(rooms) - 1):
	next = prev + 1
	px, py = (floor(rooms[prev].centerx), floor(rooms[prev].centery))
	nx, ny = (floor(rooms[next].centerx), floor(rooms[next].centery))
	if random.randint(0, 1) == 0: # Horizontal first
		for i in line_range(px, nx):
			board[i][py] = "stuff" # Horizontal
		for j in line_range(py, ny):
			board[nx][j] = "stuff" # Vertical
	else: # 						Vertical first
		for j in line_range(py, ny):
			board[px][j] = "stuff" # Vertical
		for i in line_range(px, nx):
			board[i][ny] = "stuff" # Horizontal