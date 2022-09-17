import math
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
			# We have a line of sight to this block
			if math.dist(self.pos, playerpos) > lightrange:
				self.light = 0 if self.light == 0 else 1
				return
			# We can see this block.
			self.light = 2
			for e in [p for p in ENTITIES if isinstance(p, Enemy)]:
				if random.random() < 0.1 and e.pos == self.pos:
					e.awake = True

cellsize = 10
boardsize = [*boardgen.boardsize]
BOARD = [
	[Cell([j, i], boardgen.board[i][j]) for i in range(boardsize[0])]
		for j in range(boardsize[1])
]
lightrange = 10

# ENTITIES
class Entity:
	def __init__(self, pos):
		self.pos: list = pos
		self.maxhealth: int = 10
		self.health: int = 10
	def draw(self):
		entityrect = pygame.Rect(self.pos[0] * cellsize, self.pos[1] * cellsize, cellsize, cellsize)
		pygame.draw.rect(screen, (0, 255, 255), entityrect)
		# Health bar
		barwidth = cellsize * 2.2
		barheight = cellsize * 0.7
		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(entityrect.centerx - (barwidth // 2), entityrect.top - (barheight * 2), barwidth, barheight))
		pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(entityrect.centerx - (barwidth // 2), entityrect.top - (barheight * 2), barwidth * (self.health / self.maxhealth), barheight))
	def getmove(self):
		return self.pos

class Enemy(Entity):
	def __init__(self, pos):
		super().__init__(pos)
		self.awake = False
	def draw(self):
		super().draw()
		# Sleep icon
		if not self.awake:
			i = pygame.image.load("icon-sleep.png")
			i = pygame.transform.scale(i, (cellsize, cellsize))
			screen.blit(i, (self.pos[0] * cellsize, self.pos[1] * cellsize))
	def getmove(self):
		if self.awake:
			# Pathfind to player
			if not True in [isinstance(p, Player) for p in ENTITIES]:
				player = random.choice([p for p in ENTITIES if isinstance(p, Player)])
				mat = [[BOARD[j][i].canwalk() for j in range(boardsize[1])] for i in range(boardsize[0])]
				path = pathfind(mat, self.pos, player.pos)
				if path:
					return path[1]
				else:
					return self.pos
			else:
				self.awake = False
				return self.pos
		else:
			return self.pos

class Player(Entity):
	def __init__(self, pos):
		super().__init__(pos)
		self.maxhealth = 50
		self.health = 50
	def draw(self):
		entityrect = pygame.Rect(self.pos[0] * cellsize, self.pos[1] * cellsize, cellsize, cellsize)
		pygame.draw.rect(screen, (255, 0, 0), entityrect)
		# Health bar
		barwidth = cellsize * 2.2
		barheight = cellsize * 0.7
		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(entityrect.centerx - (barwidth // 2), entityrect.top - (barheight * 2), barwidth, barheight))
		pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(entityrect.centerx - (barwidth // 2), entityrect.top - (barheight * 2), barwidth * (self.health / self.maxhealth), barheight))
	def trygetmove(self):
		if inputkey == pygame.K_UP:
			return [self.pos[0], self.pos[1] - 1]
		elif inputkey == pygame.K_DOWN:
			return [self.pos[0], self.pos[1] + 1]
		elif inputkey == pygame.K_LEFT:
			return [self.pos[0] - 1, self.pos[1]]
		elif inputkey == pygame.K_RIGHT:
			return [self.pos[0] + 1, self.pos[1]]
		elif inputkey == pygame.K_SPACE:
			# Idle
			return self.pos
	def getmove(self):
		global inputkey
		inputkey = -1
		r = None
		while ((not r) or (not BOARD[r[0]][r[1]].canwalk())) and running:
			r = self.trygetmove()
			time.sleep(0.01)
		return r

validspawn = [[x, y] for x in range(boardsize[0]) for y in range(boardsize[1]) if BOARD[x][y].canwalk()]
ENTITIES: "list[Entity]" = [Player(random.choice(validspawn)), Enemy(random.choice(validspawn))]
inputkey = -1
pygame.key.set_repeat(500, 10)

def PLAYERTHREAD():
	global running
	def lightrefresh():
		for playerpos in [e.pos for e in ENTITIES if isinstance(e, Player)]:
			for i in range(playerpos[0] - lightrange - 1, playerpos[0] + lightrange + 2):
				for j in range(playerpos[1] - lightrange - 1, playerpos[1] + lightrange + 2):
					if 0 <= i < boardsize[0] and 0 <= j < boardsize[1]:
						BOARD[i][j].refreshLight()
	def doMove(e: Entity, newX, newY):
		if BOARD[newX][newY].canwalk():
			# 1. Check for other entities
			for entity in ENTITIES:
				if entity.pos == [newX, newY]:
					entity.health -= 1
					if isinstance(entity, Enemy):
						entity.awake = True
					if entity.health <= 0:
						ENTITIES.remove(entity)
					return
			# 2. Move
			e.pos = [newX, newY]
			# 3. Light update
			lightrefresh()
	lightrefresh()
	c = pygame.time.Clock()
	while running:
		for e in ENTITIES:
			m = e.getmove()
			if running and not m == e.pos:
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
		# Drw entities
		for e in ENTITIES:
			if BOARD[e.pos[0]][e.pos[1]].light == 2:
				e.draw()
		# Flip
		pygame.display.flip()
		c.tick(60)

MAIN()