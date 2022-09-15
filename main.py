import pygame
import random
import boardgen
import threading
from line_points import get_line

WHITE = (255, 255, 255)
screensize = [500, 500]
screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
running = True

class Cell:
	def __init__(self, pos, state):
		self.pos = pos
		self.state = state
		self.light = 0 # 0 = never seen; 1 = seen before; 2 = seeing now
	def getColor(self) -> tuple:
		if self.state == "wall":
			return (255, 255, 255)
		elif self.state == "ground":
			return (0, 0, 0)
		else:
			return (255, 0, 0)
	def canwalk(self) -> bool:
		return self.state == "ground"
	def refreshLight(self):
		points = get_line(self.pos, playerpos)
		for point in points:
			if not BOARD[point[0]][point[1]].canwalk():
				self.light = 0 if self.light == 0 else 1
				return
		self.light = 2

cellsize = 10
boardsize = [*boardgen.boardsize]
BOARD = [
	[Cell((j, i), boardgen.board[i][j]) for i in range(boardsize[0])]
		for j in range(boardsize[1])
]

validspawn = [[x, y] for x in range(boardsize[0]) for y in range(boardsize[1]) if BOARD[x][y].canwalk()]
playerpos = random.choice(validspawn)
inputkey = -1
pygame.key.set_repeat(500, 10)

def PLAYERTHREAD():
	global playerpos
	global running
	needslightrefresh = [-1]
	def playerMove(newX, newY):
		global playerpos
		if BOARD[newX][newY].canwalk():
			playerpos = [newX, newY]
			if needslightrefresh[0] == -1:
				needslightrefresh[0] = 10 # Darn references
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
		# Light refresh
		if needslightrefresh[0] >= 0:
			needslightrefresh[0] -= 1
		if needslightrefresh[0] == 0:
			def lightrefresh():
				for i in range(boardsize[0]):
					for j in range(boardsize[1]):
						BOARD[i][j].refreshLight()
			threading.Thread(target=lightrefresh).start()
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
				if BOARD[i][j].light == 1:
					overlay = pygame.Surface((cellsize, cellsize))
					overlay.set_alpha(100)
					overlay.fill(BOARD[i][j].getColor())
					screen.blit(overlay, (i * cellsize, j * cellsize))
				if BOARD[i][j].light == 2:
					pygame.draw.rect(screen, BOARD[i][j].getColor(), pygame.Rect(i * cellsize, j * cellsize, cellsize, cellsize))
		# Player
		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(playerpos[0] * cellsize, playerpos[1] * cellsize, cellsize, cellsize))
		# Flip
		pygame.display.flip()
		c.tick(60)

MAIN()