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
		seen = False
		for playerpos in [p.pos for p in ENTITIES if isinstance(p, Player)]:
			points = get_line(self.pos, playerpos)
			isblocked = False
			for point in points:
				if not BOARD[point[0]][point[1]].canwalk():
					isblocked = True
			# We have a line of sight to this block
			if math.dist(self.pos, playerpos) > lightrange:
				isblocked = True
			if not isblocked:
				seen = True
		if seen:
			# We can see this block.
			self.light = 2
			for e in [p for p in ENTITIES if isinstance(p, Enemy)]:
				if random.random() < 0.1 and e.pos == self.pos:
					e.awake = True
		else:
			self.light = 0 if self.light == 0 else 1

cellsize = 10
boardsize = [*boardgen.boardsize]
BOARD = [
	[Cell([j, i], boardgen.board[i][j]) for i in range(boardsize[0])]
		for j in range(boardsize[1])
]
lightrange = 10

# get_attack_target determines if a target walking position represents an attack on another entity.
# If it is, then it will return the attacked entity, otherwise it returns None.
def get_attack_target(source_entity, target_pos) -> "Entity | None":
	if target_pos == None: return None
	if BOARD[target_pos[0]][target_pos[1]].canwalk():
		for e in ENTITIES:
			if not e == source_entity and e.pos == target_pos:
				return e
	return None

def lightrefresh():
	doneCells = []
	for playerpos in [e.pos for e in ENTITIES if isinstance(e, Player)]:
		for i in range(playerpos[0] - lightrange - 1, playerpos[0] + lightrange + 2):
			for j in range(playerpos[1] - lightrange - 1, playerpos[1] + lightrange + 2):
				if [i, j] not in doneCells and 0 <= i < boardsize[0] and 0 <= j < boardsize[1]:
					BOARD[i][j].refreshLight()
					doneCells.append([i, j])

# ENTITIES
class Entity:
	def __init__(self, pos):
		self.pos: list = pos
		self.maxhealth: int = 10
		self.health: int = 10
		self.time = max([e.time for e in ENTITIES]) if len(ENTITIES) > 0 else 0
		self.focused = False
	def draw(self):
		entityrect = pygame.Rect(self.pos[0] * cellsize, self.pos[1] * cellsize, cellsize, cellsize)
		pygame.draw.rect(screen, (0, 255, 255), entityrect)
		# Health bar
		barwidth = cellsize * 2.2
		barheight = cellsize * 0.7
		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(entityrect.centerx - (barwidth // 2), entityrect.top - (barheight * 2), barwidth, barheight))
		pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(entityrect.centerx - (barwidth // 2), entityrect.top - (barheight * 2), barwidth * (self.health / self.maxhealth), barheight))
		# Focus
		if self.focused:
			pygame.draw.rect(screen, (255, 255, 0), entityrect, 2)
	def getmove(self):
		return self.pos
	def doaction(self):
		next_pos = self.getmove()
		target = get_attack_target(self, next_pos)
		if target:
			target.health -= 1
			self.time += 1
			return
		else:
			self.pos = next_pos
			self.time += 1

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
			if True in [isinstance(p, Player) for p in ENTITIES]:
				player = random.choice([p for p in ENTITIES if isinstance(p, Player)])
				mat = [[BOARD[j][i].canwalk() for j in range(boardsize[1])] for i in range(boardsize[0])]
				path = pathfind(mat, self.pos, player.pos)
				if path and len(path) > 1:
					return [*path[1]]
				else:
					return self.pos
			else:
				self.awake = False
				return self.pos
		else:
			return self.pos
	def doaction(self):
		next_pos = self.getmove()
		target = get_attack_target(self, next_pos)
		if target:
			target.health -= 1
			self.time += 1
			return
		else:
			self.pos = next_pos
			self.time += 1

class Player(Entity):
	def __init__(self, pos):
		super().__init__(pos)
		self.maxhealth = 50
		self.health = 50
		self.target = None
	def draw(self):
		entityrect = pygame.Rect(self.pos[0] * cellsize, self.pos[1] * cellsize, cellsize, cellsize)
		pygame.draw.rect(screen, (255, 0, 0), entityrect)
		# Health bar
		barwidth = cellsize * 2.2
		barheight = cellsize * 0.7
		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(entityrect.centerx - (barwidth // 2), entityrect.top - (barheight * 2), barwidth, barheight))
		pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(entityrect.centerx - (barwidth // 2), entityrect.top - (barheight * 2), barwidth * (self.health / self.maxhealth), barheight))
		# Focus
		if self.focused:
			pygame.draw.rect(screen, (255, 255, 0), entityrect, 2)
	def trygetmove(self):
		if self.target:
			# Pathfind to target
			if self.pos == self.target:
				self.target = None
				return
			mat = [[BOARD[j][i].canwalk() for j in range(boardsize[1])] for i in range(boardsize[0])]
			path = pathfind(mat, self.pos, self.target)
			if path and len(path) > 1:
				return [*path[1]]
			else:
				self.target = None
				return
		elif inputkey == pygame.K_UP:
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
		global clickpos
		inputkey = -1
		clickpos = None
		chosenpos = None
		while ((not chosenpos) or (not BOARD[chosenpos[0]][chosenpos[1]].canwalk())) and running:
			chosenpos = self.trygetmove()
			time.sleep(0.01)
			if clickpos:
				self.target = clickpos
				clickpos = None
		return chosenpos
	def doaction(self):
		next_pos = self.getmove()
		target = get_attack_target(self, next_pos)
		if target:
			target.health -= 1
			self.time += 0.5
			return
		elif next_pos:
			self.pos = next_pos
			self.time += 1
			lightrefresh()

validspawn = [[x, y] for x in range(boardsize[0]) for y in range(boardsize[1]) if BOARD[x][y].canwalk()]
ENTITIES: "list[Entity]" = []
ENTITIES.append(Player(random.choice(validspawn)))
ENTITIES.append(Player(random.choice(validspawn)))
ENTITIES.append(Player(random.choice(validspawn)))
ENTITIES.append(Player(random.choice(validspawn)))
ENTITIES.append(Player(random.choice(validspawn)))
ENTITIES.append(Player(random.choice(validspawn)))
ENTITIES.append(Enemy(random.choice(validspawn)))
inputkey = -1
pygame.key.set_repeat(500, 10)
clickpos = None

def GAMETHREAD():
	global running
	lightrefresh()
	c = pygame.time.Clock()
	while running:
		for e in [*ENTITIES]:
			e.focused = True
			e.doaction()
			if e.health <= 0:
				ENTITIES.remove(e)
			e.focused = False
		c.tick(60)

def MAIN():
	global screen
	global running
	global inputkey
	global clickpos
	threading.Thread(target=GAMETHREAD).start()
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
			elif event.type == pygame.MOUSEBUTTONDOWN:
				clickpos = [event.pos[0] // cellsize, event.pos[1] // cellsize]
				if BOARD[clickpos[0]][clickpos[1]].light == 0:
					clickpos = None
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
