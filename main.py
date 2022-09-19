import math
import pygame
import random
import boardgen
import threading
from line_points import get_line
import time
from pathfind import pathfind

cellsize = 10
WHITE = (255, 255, 255)
screensize = [boardgen.boardsize[0] * cellsize, boardgen.boardsize[1] * cellsize]
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

def lightrefreshall():
	if pygame.key.get_pressed()[pygame.K_q]: return
	for i in range(boardsize[0]):
		for j in range(boardsize[1]):
			for player in [e for e in ENTITIES if isinstance(e, Player)]:
				BOARD[i][j].refreshLight()

# ENTITIES
class Entity:
	def __init__(self, pos):
		self.pos: list = pos
		self.maxhealth: int = 10
		self.health: int = 10
		self.time = max([e.time for e in ENTITIES]) if len(ENTITIES) > 0 else 0
		self.focused = False
		self.healtime = 0
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
			screen.blit(i, ((self.pos[0] + 0.7) * cellsize, (self.pos[1] - 0.7) * cellsize))
	def getmove(self):
		if self.awake:
			# Pathfind to player
			if True in [isinstance(p, Player) for p in ENTITIES]:
				mat = [[BOARD[j][i].canwalk() for j in range(boardsize[1])] for i in range(boardsize[0])]
				closestplayer = min([p for p in ENTITIES if isinstance(p, Player)], key=lambda p: len(pathfind(mat, p.pos, self.pos)))
				path = pathfind(mat, self.pos, closestplayer.pos)
				if path and len(path) > 1:
					return [*path[1]]
				else:
					return self.pos
			else:
				r = random.choice([
					[self.pos[0] + 1, self.pos[1]],
					[self.pos[0] - 1, self.pos[1]],
					[self.pos[0], self.pos[1] + 1],
					[self.pos[0], self.pos[1] - 1]
				])
				if BOARD[r[0]][r[1]].canwalk():
					return r
				else:
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
		global isprogress
		inputkey = -1
		clickpos = None
		chosenpos = None
		while ((not chosenpos) or (not BOARD[chosenpos[0]][chosenpos[1]].canwalk())) and running:
			chosenpos = self.trygetmove()
			time.sleep(0.01)
			if clickpos:
				self.target = clickpos
				clickpos = None
			isprogress = False
		isprogress = True
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

class FastPlayer(Player):
	def doaction(self):
		next_pos = self.getmove()
		target = get_attack_target(self, next_pos)
		if target:
			target.health -= 1
			self.time += 0.4
			return
		elif next_pos:
			self.pos = next_pos
			self.time += 0.1
			lightrefresh()

validspawn = [[x, y] for x in range(boardsize[0]) for y in range(boardsize[1]) if BOARD[x][y].canwalk()]
ENTITIES: "list[Entity]" = []
ENTITIES.append(FastPlayer(random.choice(validspawn)))
[ENTITIES.append(Enemy(random.choice(validspawn))) for x in range(30)];
inputkey = -1
pygame.key.set_repeat(500, 10)
clickpos = None
playerspawntime = 0
isprogress = True

def GAMETHREAD():
	global running
	global playerspawntime
	lightrefresh()
	c = pygame.time.Clock()
	while running:
		# Find list of entities that have lowest time value
		l = min([e.time for e in ENTITIES])
		for e in [e for e in ENTITIES if e.time <= l]:
			e.focused = True
			e.doaction()
			e.focused = False
			# Natural healing
			if e.health < e.maxhealth:
				if e.healtime == 0:
					e.health += 1
					e.healtime = 20
				else:
					e.healtime -= 1
			for e in ENTITIES:
				if e.health <= 0:
					ENTITIES.remove(e)
					lightrefreshall()
		# Spawn player?
		if playerspawntime == 0:
			t = random.choice(validspawn)
			if not get_attack_target(None, t):
				playerspawntime = 250
				ENTITIES.append(Player(t))
				for i in range(5): ENTITIES.append(Enemy(random.choice(validspawn)))
				lightrefreshall()
		else:
			playerspawntime -= 1
		c.tick(60)

def MAIN():
	global screen
	global running
	global inputkey
	global clickpos
	global screensize
	threading.Thread(target=GAMETHREAD).start()
	progresstime = 0
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
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_q:
					lightrefreshall()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				clickpos = [event.pos[0] // cellsize, event.pos[1] // cellsize]
				if clickpos[0] >= boardsize[0] or clickpos[1] >= boardsize[1]:
					clickpos = None
				elif BOARD[clickpos[0]][clickpos[1]].light == 0:
					clickpos = None
		screen.fill(WHITE)
		# Board
		if not pygame.key.get_pressed()[pygame.K_q]:
			for i in range(boardsize[0]):
				for j in range(boardsize[1]):
					if BOARD[i][j].light == 1:
						overlay = pygame.Surface((cellsize, cellsize))
						overlay.set_alpha(100)
						overlay.fill(BOARD[i][j].getColor())
						screen.blit(overlay, (i * cellsize, j * cellsize))
					if BOARD[i][j].light == 2:
						pygame.draw.rect(screen, BOARD[i][j].getColor(), pygame.Rect(i * cellsize, j * cellsize, cellsize, cellsize))
		# Draw entities
		for e in ENTITIES:
			if BOARD[e.pos[0]][e.pos[1]].light == 2:
				e.draw()
		# Progress indicator
		if isprogress:
			progresstime += 5
			ind = pygame.Surface((screensize[0] // 10, screensize[1] // 10), pygame.SRCALPHA)
			ind.fill((0, 0, 0, 0))
			pygame.draw.circle(ind, (0, 0, 0, 100), (ind.get_width() // 2, ind.get_height() // 2), min(ind.get_width(), ind.get_height()) // 2)
			pygame.draw.rect(ind, (0, 0, 0, 0), pygame.Rect(0, 0, ind.get_width() // 2, ind.get_height() // 2))
			pygame.draw.rect(ind, (0, 0, 0, 0), pygame.Rect(ind.get_width() // 2, ind.get_height() // 2, ind.get_width() // 2, ind.get_height() // 2))
			rot = pygame.transform.rotate(ind, -progresstime)
			rot_cropped = pygame.Surface((screensize[0] // 10, screensize[1] // 10), pygame.SRCALPHA)
			rot_cropped.blit(rot, ((screensize[0] // 20) - (rot.get_width() // 2), (screensize[1] // 20) - (rot.get_height() // 2)))
			screen.blit(rot_cropped, (0, 0))
		else:
			progresstime = 0
		# Flip
		pygame.display.flip()
		c.tick(60)

MAIN()
