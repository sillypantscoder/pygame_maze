import pygame
import threading
import random
import boardgen_points as boardgen
from boardconst import *
import pathfind

pygame.font.init()

# Colors
BACKGROUND = (0, 0, 0)
TEXTCOLOR = (255, 255, 255)
TILEEMPTY = (30, 30, 200)
TILEWALL = (255, 40, 40)
TILEDOOR = (217, 106, 22)
TILEBOARDWALK = (102, 53, 34)
PLAYERCOLOR = (0, 0, 0)

# Setup
ZOOM = 50
BOARD = [
	[
		{"state": state, "light": True}
			for state in row
	] for row in boardgen.board
]
FONT = pygame.font.SysFont("monospace", 30)
FONTHEIGHT = FONT.render("0", True, TEXTCOLOR).get_height()
validspawn = [(x, y) for x in range(len(BOARD[0])) for y in range(len(BOARD)) if BOARD[y][x]["state"] == 1]
playerpos = [*random.choice(validspawn)]
SCREENSIZE = [500, 500 + FONTHEIGHT]
maxhealth = 10
health = maxhealth + 0
ROUTE: "list[Action]" = []

# Textures
TEXTURES: "list[pygame.Surface]" = []
DARKTEXTURES: "list[pygame.Surface]" = []
colors = [(0, 0, 0), (30, 30, 200), (255, 40, 40), (217, 106, 22), (102, 53, 34)]
for i in ALLBLOCKS:
	TEXTURES.append(None)
	TEXTURES[i] = pygame.Surface([ZOOM, ZOOM])
	TEXTURES[i].fill(colors[i])
	DARKTEXTURES.append(TEXTURES[i].copy())
	# Dim the texture.
	s = pygame.Surface([ZOOM, ZOOM], pygame.SRCALPHA)
	s.fill((0, 0, 0, 200))
	DARKTEXTURES[i].blit(s, (0, 0))

class Action:
	def __init__(self, to: "Monster | None" = None):
		self.to = to
	def run(self):
		pass

class MoveAction(Action):
	def __init__(self, to: "Monster | None" = None, pos: "tuple[int, int]" = (0, 0)):
		super().__init__(to)
		self.pos = pos
	def run(self):
		global playerpos
		if self.to != None:
			self.to.x, self.to.y = self.pos
		else:
			playerpos = [*self.pos]

class Monster:
	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y
		self.action: "Action | None" = None
	def frame(self):
		global health
		# Check if we need to figure out what to do next
		if self.action == None:
			self.newaction()
		# Ok then
		self.action.run()
		self.action = None
	def newaction(self):
		global health
		# Pathfind to player
		path = pathfind.pathfind(boardgen.board, (self.x, self.y), playerpos)
		if path:
			if len(path) > 2:
				# Move towards player
				self.action = MoveAction(self, path[1])
			else:
				# We're at the player, attack!
				self.action = Action(self)
				# ...probably implement something like "AttackAction" later
		else:
			# can't find the player...
			if self in ENTITIES: ENTITIES.remove(self)
			self.action = Action(self)
			# so we kill ourselves. logical course of action.
			print("Monster died")
	def draw(self, screen, offset):
		# Check if we're on a hidden tile
		if not BOARD[self.y][self.x]["light"]:
			return
		pygame.draw.circle(screen, PLAYERCOLOR, ((self.x * ZOOM) + offset[0] + (ZOOM // 2), (self.y * ZOOM) + offset[1] + (ZOOM // 2)), ZOOM // 2)

ENTITIES = [Monster(*random.choice(validspawn)) for x in range(10)]

def insideBoard(x: int, y: int) -> bool:
	"""Checks whether the given coordinates are inside the board."""
	return (0 <= x < len(BOARD[0])) and (0 <= y < len(BOARD))

def getPlayerBlock() -> "dict[str, int] | None":
	"""Returns the block the player is on."""
	try:
		return BOARD[playerpos[1]][playerpos[0]]
	except IndexError:
		return None

def playerMove(direction: str) -> None:
	"""Moves the player in the given direction."""
	if direction == "up" and playerpos[1] > 0:
		playerpos[1] -= 1
		if getPlayerBlock()["state"] in WALLBLOCKS: playerpos[1] += 1
	elif direction == "down" and playerpos[1] < len(BOARD) - 1:
		playerpos[1] += 1
		if getPlayerBlock()["state"] in WALLBLOCKS: playerpos[1] -= 1
	elif direction == "left" and playerpos[0] > 0:
		playerpos[0] -= 1
		if getPlayerBlock()["state"] in WALLBLOCKS: playerpos[0] += 1
	elif direction == "right" and playerpos[0] < len(BOARD[0]) - 1:
		playerpos[0] += 1
		if getPlayerBlock()["state"] in WALLBLOCKS: playerpos[0] -= 1

def addBlock(x: int, y: int) -> None:
	"""Adds a block to the board."""
	global portalroom
	s = newBlockState(x, y)
	if s == 3: portalroom = True
	BOARD.append({"x": x, "y": y, "state": s, "light": True})

def newBlockState(x: int, y: int) -> int:
	"""Generates a new block state."""
	try:
		return BOARD[y][x]
	except IndexError:
		return 1

def checkLight():
	"""Checks whether the player has a line of sight for each block."""
	from line_points import get_line as get_line_points
	# Iterate over every block
	for y in range(len(BOARD)):
		for x in range(len(BOARD[y])):
			block = BOARD[y][x]
			# Check whether the player has a line of sight to the block.
			# 1. Get list of points from player to block.
			p = get_line_points((playerpos[0], playerpos[1]), (x, y))
			# 3. Check whether any of the points are walls.
			walls = 0
			for point in p:
				b = BOARD[point[1]][point[0]]
				# Make sure we are not checking the target block or the player position.
				if point != (x, y) and [*point] != playerpos:
					# Check if the block is a wall.
					if b["state"] not in SEETHROUGHBLOCKS:
						walls += 1
			# 4. If there are no walls, set the block to light.
			block["light"] = walls == 0

screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
pygame.key.set_repeat(300, 50)

c = pygame.time.Clock()
running = True
checkLight()
while running:
	clicked = None
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			SCREENSIZE = event.size
			screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				playerMove("up")
			elif event.key == pygame.K_DOWN:
				playerMove("down")
			elif event.key == pygame.K_LEFT:
				playerMove("left")
			elif event.key == pygame.K_RIGHT:
				playerMove("right")
		elif event.type == pygame.MOUSEBUTTONDOWN:
			clicked = pygame.mouse.get_pos()
	# Route
	if len(ROUTE) > 0:
		ROUTE.pop(0).run()
		# Tick the entities
		for entity in ENTITIES:
			entity.frame()
		checkLight()
	# Drawing
	offset = [(SCREENSIZE[0] / 2) + (ZOOM / -2) + (playerpos[0] * -ZOOM), (SCREENSIZE[1] / 2) + (ZOOM / -2) + (playerpos[1] * -ZOOM)]
	screen.fill(BACKGROUND)
	for y in range(len(BOARD)):
		for x in range(len(BOARD[y])):
			cell = BOARD[y][x]
			# Draw the cell
			cellrect = pygame.Rect(x * ZOOM, y * ZOOM, ZOOM, ZOOM)
			cellrect.move_ip(*offset)
			player_on = (x == playerpos[0]) and (y == playerpos[1])
			screen.blit((TEXTURES if cell["light"] else DARKTEXTURES)[cell["state"]], cellrect)
			# Pathfinding
			if clicked and cellrect.collidepoint(clicked):
				# Find a path to the block
				path = pathfind.pathfind(boardgen.board, playerpos, (x, y))
				# Move the player
				if path != None:
					for p in path[1:]:
						ROUTE.append(MoveAction(None, p))
	# Draw the entities
	for entity in ENTITIES:
		entity.draw(screen, offset)
	# Draw the player
	playerrect = pygame.Rect((playerpos[0] * ZOOM) + (ZOOM / 3), (playerpos[1] * ZOOM) + (ZOOM / 3), ZOOM / 3, ZOOM / 3)
	playerrect.move_ip(*offset)
	pygame.draw.rect(screen, PLAYERCOLOR, playerrect)
	# Add health bar
	toolbarrect = pygame.Rect(0, SCREENSIZE[1] - FONTHEIGHT, SCREENSIZE[0], FONTHEIGHT)
	pygame.draw.rect(screen, BACKGROUND, toolbarrect)
	healthbarrect = toolbarrect.copy()
	healthbarrect.width = healthbarrect.width * (health / maxhealth)
	pygame.draw.rect(screen, TEXTCOLOR, healthbarrect)
	# Flip
	pygame.display.flip()
	c.tick(60)
