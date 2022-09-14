import pygame
import random
import boardgen
import threading

WHITE = (255, 255, 255)
screensize = [500, 500]
screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
running = True

cellsize = 10
boardsize = [*boardgen.boardsize]
BOARD = [
	[boardgen.board[i][j] for i in range(boardsize[0])]
		for j in range(boardsize[1])
]

validspawn = [[x, y] for x in range(boardsize[0]) for y in range(boardsize[1]) if BOARD[x][y] == "ground"]
playerpos = random.choice(validspawn)
inputkey = -1
pygame.key.set_repeat(500, 10)

def draw(t, rect):
	if t == "wall":
		pygame.draw.rect(screen, WHITE, rect)
	elif t == "ground":
		pygame.draw.rect(screen, (0, 0, 0), rect)
	else:
		raise Exception(f"Dunno what {t} is, something's wrong :/")

def PLAYERTHREAD():
	global playerpos
	global running
	def playerMove(newX, newY):
		global playerpos
		if BOARD[newX][newY] == "ground":
			playerpos = [newX, newY]
	c = pygame.time.Clock()
	while running:
		if inputkey == pygame.K_UP:
			playerMove(playerpos[0], playerpos[1] - 1)
		elif inputkey == pygame.K_DOWN:
			playerMove(playerpos[0], playerpos[1] + 1)
		elif inputkey == pygame.K_LEFT:
			playerMove(playerpos[0] - 1, playerpos[1])
		elif inputkey == pygame.K_RIGHT:
			playerMove(playerpos[0] + 1, playerpos[1])
		c.tick(60)

def MAIN():
	global screen
	global running
	global inputkey
	threading.Thread(target=PLAYERTHREAD).start()
	running = True
	c = pygame.time.Clock()
	while running:
		inputkey = -1
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.VIDEORESIZE:
				screensize = event.size
				screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
			elif event.type == pygame.KEYDOWN:
				inputkey = event.key
		screen.fill(WHITE)
		# Board
		for i in range(boardsize[0]):
			for j in range(boardsize[1]):
				draw(BOARD[i][j], pygame.Rect(i * cellsize, j * cellsize, cellsize, cellsize))
		# Player
		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(playerpos[0] * cellsize, playerpos[1] * cellsize, cellsize, cellsize))
		# Flip
		pygame.display.flip()
		c.tick(60)

MAIN()