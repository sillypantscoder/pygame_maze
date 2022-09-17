import pygame
import random
import boardgen
import threading
from line_points import get_line
import time
from pathfind import pathfind

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
		for playerpos in [p.pos for p in ENTITIES if isinstance(p, Player)]:
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
lightrefreshtime = [-1]

# ENTITIES
class Entity:
	def __init__(self, pos):
		self.pos: list = pos
	def draw(self):
		pygame.draw.rect(screen, (0, 255, 255), pygame.Rect(self.pos[0] * cellsize, self.pos[1] * cellsize, cellsize, cellsize))
	def getmove(self):
		return self.pos

class BadThing(Entity):
	def getmove(self):
		# Pathfind to player
		player = random.choice([p for p in ENTITIES if isinstance(p, Player)])
		mat = [[BOARD[j][i].canwalk() for j in range(boardsize[1])] for i in range(boardsize[0])]
		path = pathfind(mat, self.pos, player.pos)
		if path:
			return path[1]
		else:
			return self.pos

class Player(Entity):
	def draw(self):
		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(self.pos[0] * cellsize, self.pos[1] * cellsize, cellsize, cellsize))
	def trygetmove(self):
		if inputkey == pygame.K_UP:
			return [self.pos[0], self.pos[1] - 1]
		elif inputkey == pygame.K_DOWN:
			return [self.pos[0], self.pos[1] + 1]
		elif inputkey == pygame.K_LEFT:
			return [self.pos[0] - 1, self.pos[1]]
		elif inputkey == pygame.K_RIGHT:
			return [self.pos[0] + 1, self.pos[1]]
	def getmove(self):
		global inputkey
		inputkey = -1
		r = None
		while ((not r) or (not BOARD[r[0]][r[1]].canwalk())) and running:
			r = self.trygetmove()
			time.sleep(0.01)
		return r

validspawn = [[x, y] for x in range(boardsize[0]) for y in range(boardsize[1]) if BOARD[x][y].canwalk()]
ENTITIES: "list[Entity]" = [Player(random.choice(validspawn)), BadThing(random.choice(validspawn))]
inputkey = -1
pygame.key.set_repeat(500, 10)

def PLAYERTHREAD():
	global running
	global lightrefreshtime
	lightrefreshtime = [1]
	def doMove(e: Entity, newX, newY):
		if BOARD[newX][newY].canwalk():
			e.pos = [newX, newY]
			if isinstance(e, Player) and lightrefreshtime[0] == -1:
				lightrefreshtime[0] = 20
	c = pygame.time.Clock()
	while running:
		for e in ENTITIES:
			m = e.getmove()
			if running:
				doMove(e, *m)
		c.tick(60)

def MAIN():
	global screen
	global running
	global inputkey
	threading.Thread(target=PLAYERTHREAD).start()
	running = True
	c = pygame.time.Clock()
	while running:
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
		for e in ENTITIES:
			e.draw()
		# Light refresh
		if lightrefreshtime[0] >= 0:
			lightrefreshtime[0] -= 1
		if lightrefreshtime[0] == 0:
			def lightrefresh():
				for i in range(boardsize[0]):
					for j in range(boardsize[1]):
						BOARD[i][j].refreshLight()
			threading.Thread(target=lightrefresh).start()
		# Flip
		pygame.display.flip()
		c.tick(60)

MAIN()