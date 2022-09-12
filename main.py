import pygame
import random
import boardgen_points as boardgen
from boardconst import *
import pathfind
import json
import os
import base64
import io

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
maxhealth = 20
health = maxhealth + 0
TARGET: "list[int]" = [*playerpos]
INVENTORY: "list[Item]" = []
ITEMS: "list[DroppedItem]" = []
INVENTORY_MAINHAND = None
ITEMDEFS = {}
for f in os.listdir("items"):
	i = open("items/" + f, "r")
	ITEMDEFS[f[:-4]] = json.loads(i.read())
	i.close()
TIME = 0

def getPathfindingBoard():
	"""Returns a list of lists of integers representing the board."""
	def isValidCell(x: int, y: int) -> bool:
		"""Checks whether the given cell is valid."""
		for e in ENTITIES:
			if e.x == x and e.y == y:
				return False
		return BOARD[y][x]["state"] not in WALLBLOCKS
	return [[isValidCell(x, y) for x in range(len(BOARD[y]))] for y in range(len(BOARD))]

# Textures

def base64ToSurface(b: str) -> pygame.Surface:
	"""Converts a base64 string to a pygame surface."""
	data = base64.b64decode(b)
	img = pygame.image.load(io.BytesIO(data), ".png")
	return img

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

class Monster:
	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y
		self.health = maxhealth // 5
		self.time = TIME + 1
		self.texture = base64ToSurface("iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAAAXNSR0IArs4c6QAAAdVJREFUaEPtmOGSwjAIhPX9H9obO9ZLUgjLAq3Tyf07TQgfC4T4fNzk73kTjscC+TUllyKKIi+nUmmBZAypzgYoGD+6mHkNvLzOIgp9nPD6QoNsDBUgb7sNBQWEbipRQlKLBbJASlWYpZ033UyQqlTKrh0N5DIlRkBUGRXkTCV2J7QzERgJRC1s60AkXZSIbx9ngky7U0udpRgaHEuVURGzzaIHI+p4AzOD6WwhUfYergExdlJBhluYvukZZdNBWhhERabAJ7e+2Gm7wHicYlJjdy5h7wHm/cHXfw9IJMWYtBqCoIN4IUaQysm4TTOtTjZFGAjBOF34SKuGFImCeByJri1VJOqcZ/8C8UTrjLVLEU+UxTeBxwCwtlQRcWYQnMrojjOQ7S5jDtEAdlvW94AAhyWpIIyDh4cPQ/H/+5c4ouwmIVUiDkWGxWYkmk6/EEwEYpx8A6mcC8I4kvSOgUCmhR8Zv8mS6LahL8R2k1gvV4LMIKQnRQdz1hsDUSsC8m0AVwNZEJYiY6Au+z04GwRq0UiaoGua9mROQeYCaWRiWy8KMNw5kI/QIm3+qwLyKDFetN5gdY1A/IewyABkgYgNgWAI+8OmVsDXmq0LpCauvNXbKPIHEVtxMxbvwcwAAAAASUVORK5CYIIA")
	def frame(self):
		global health
		while self.time <= TIME:
			self.doaction()
		# Check if we're dead
		if self.health <= 0:
			self.die()
			print("Monster died...")
	def die(self):
		if self in ENTITIES: ENTITIES.remove(self)
		self.time += 10
	def doaction(self):
		global health
		global TARGET
		# Pathfind to player
		path = pathfind.pathfind(getPathfindingBoard(), (self.x, self.y), playerpos)
		if path:
			if len(path) > 2:
				# Move towards player
				self.x, self.y = path[1]
				self.time += 1
			else:
				# We're at the player, attack!
				health -= 1
				self.time += 1.5
		else:
			# can't find the player...
			self.die()
			# so we kill ourselves. logical course of action.
			print("Monster died")
	def draw(self, screen: pygame.Surface, offset):
		# Check if we're on a hidden tile
		if not BOARD[self.y][self.x]["light"]:
			return
		screen.blit(self.texture, ((self.x * ZOOM) + offset[0], (self.y * ZOOM) + offset[1]))

def addItemStackToPlayerInventory(item: "Item"):
	numLeftToAdd = item.stacksize
	maxStack = item.getdef()["stacksize"]
	for existing in INVENTORY:
		if existing.name == item.name:
			space = maxStack - existing.stacksize
			toAdd = min(space, numLeftToAdd)
			existing.stacksize += toAdd
			numLeftToAdd -= toAdd
			if numLeftToAdd == 0:
				return
	INVENTORY.append(item)

def addItemToPlayerInventory(item: "Item"):
	if not item:
		return # sometimes we get None when adding extra items
	for i in INVENTORY:
		if i.name == item.name and i.stacksize < i.getdef()["stacksize"]:
			i.stacksize += item.stacksize
			extras = i.chop_extra_items()
			if extras:
				INVENTORY.append(extras)
			return
	INVENTORY.append(item)

class Item:
	def __init__(self, name, stacksize: int = 1):
		self.name = name
		self.stacksize = stacksize
	def draw(self):
		s = base64ToSurface(self.getdef()["texture"])
		return s
	def getdef(self):
		return ITEMDEFS[self.name]
	def chop_extra_items(self):
		"""Checks whether we have too many items in this stack. Chops off the extras and returns the remaining items."""
		if self.stacksize > self.getdef()["stacksize"]:
			returnItem = Item(self.name, self.stacksize - self.getdef()["stacksize"])
			self.stacksize = self.getdef()["stacksize"]
			return returnItem

class DroppedItem:
	def __init__(self, pos: "list[int]", i: Item):
		self.item = i
		self.x, self.y = pos
	def collect(self):
		addItemToPlayerInventory(self.item)
		ITEMS.remove(self)
	def draw(self, screen: pygame.Surface, offset):
		if not BOARD[self.y][self.x]["light"]:
			return
		screen.blit(self.item.draw(), ((self.x * ZOOM) + offset[0], (self.y * ZOOM) + offset[1]))

def newItem():
	i = random.choices([n for n in ITEMDEFS.keys()], weights=[n["chance"] for n in ITEMDEFS.values()], k=1)[0]
	ITEMS.append(DroppedItem(random.choice(validspawn), Item(i)))

ENTITIES = [Monster(*random.choice(validspawn)) for x in range(10)]
[newItem() for i in range(20)];

def insideBoard(x: int, y: int) -> bool:
	"""Checks whether the given coordinates are inside the board."""
	return (0 <= x < len(BOARD[0])) and (0 <= y < len(BOARD))

def getPlayerBlock() -> "dict[str, int] | None":
	"""Returns the block the player is on."""
	try:
		return BOARD[playerpos[1]][playerpos[0]]
	except IndexError:
		return None

def isCellThatPlayerCanMoveInto(pos):
	x, y = pos
	return BOARD[y][x]["state"] not in WALLBLOCKS

def posAfterMoved(pos, dir):
	if dir == "up":
		return [pos[0], pos[1]-1]
	elif dir == "down":
		return [pos[0], pos[1]+1]
	elif dir == "left":
		return [pos[0]-1, pos[1]]
	elif dir == "right":
		return [pos[0]+1, pos[1]]

def finalPlayerPos():
	return TARGET

def playerMove(direction: str) -> None:
	"""Moves the player in the given direction."""
	global TARGET
	newPos = posAfterMoved(finalPlayerPos(), direction)
	if not isCellThatPlayerCanMoveInto(newPos):
		return
	TARGET = [*newPos]

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

def DIALOG_INVENTORY():
	global screen
	global SCREENSIZE
	global INVENTORY_MAINHAND
	c = pygame.time.Clock()
	running = True
	while running:
		clicked = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			elif event.type == pygame.VIDEORESIZE:
				SCREENSIZE = event.size
				screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return True
			elif event.type == pygame.MOUSEBUTTONDOWN:
				clicked = True
		# Background
		p = pygame.Surface((SCREENSIZE[0], SCREENSIZE[1]), pygame.SRCALPHA)
		p.fill((255, 255, 255, 1))
		screen.blit(p, (0, 0))
		# Header
		pygame.draw.rect(screen, BACKGROUND, pygame.Rect(0, 0, SCREENSIZE[0], FONTHEIGHT))
		screen.blit(FONT.render("Inventory", True, TEXTCOLOR), (0, 0))
		# Grid
		num_cols = 4
		cell_size = SCREENSIZE[0] // num_cols
		# Main hand
		if INVENTORY_MAINHAND:
			row = 0 // num_cols
			col = 0 % num_cols
			x = col * cell_size
			y = FONTHEIGHT + (row * cell_size)
			cellrect = pygame.Rect(x, y, cell_size, cell_size)
			pygame.draw.rect(screen, TEXTCOLOR, cellrect)
			screen.blit(INVENTORY_MAINHAND.draw(), (x, y))
			# Text
			if INVENTORY_MAINHAND.stacksize > 1:
				t = FONT.render(f"(x{INVENTORY_MAINHAND.stacksize})", True, TILEBOARDWALK)
				screen.blit(t, (x + cell_size - t.get_width(), y + cell_size - t.get_height()))
			if cellrect.collidepoint(pygame.mouse.get_pos()):
				pygame.draw.rect(screen, BACKGROUND, pygame.Rect(0, 0, SCREENSIZE[0], FONTHEIGHT))
				screen.blit(FONT.render(f"- In Main Hand - {INVENTORY_MAINHAND.getdef()['name']}", True, TEXTCOLOR), (0, 0))
				if clicked:
					addItemToPlayerInventory(INVENTORY_MAINHAND)
					INVENTORY_MAINHAND = None
		# Rest of inventory
		for i in [i + 1 for i in range(len(INVENTORY))]:
			row = i // num_cols
			col = i % num_cols
			x = col * cell_size
			y = FONTHEIGHT + (row * cell_size)
			cellrect = pygame.Rect(x, y, cell_size, cell_size)
			if cellrect.collidepoint(pygame.mouse.get_pos()):
				pygame.draw.rect(screen, TEXTCOLOR, cellrect)
				pygame.draw.rect(screen, BACKGROUND, pygame.Rect(0, 0, SCREENSIZE[0], FONTHEIGHT))
				screen.blit(FONT.render(f"- {INVENTORY[i - 1].getdef()['name']}", True, TEXTCOLOR), (0, 0))
				if clicked and not INVENTORY_MAINHAND and ITEMDEFS[INVENTORY[i - 1].name]["type"] == "melee":
					INVENTORY_MAINHAND = INVENTORY[i - 1]
					INVENTORY.remove(INVENTORY[i - 1])
					break
			else:
				pygame.draw.rect(screen, BACKGROUND, cellrect)
				pygame.draw.rect(screen, TEXTCOLOR, cellrect, 1)
			# Text
			if INVENTORY[i - 1].stacksize > 1:
				t = FONT.render(f"(x{INVENTORY[i - 1].stacksize})", True, TILEBOARDWALK)
				screen.blit(t, (x + cell_size - t.get_width(), y + cell_size - t.get_height()))
			# Item
			screen.blit(INVENTORY[i - 1].draw(), (x, y))
		# Flip
		pygame.display.flip()
		c.tick(60)
	return True

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
			elif event.key == pygame.K_e:
				running = DIALOG_INVENTORY()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			clicked = pygame.mouse.get_pos()
	# Route
	route = pathfind.pathfind(boardgen.board, playerpos, TARGET)
	if route and len(route) > 2:
		playerpos = [*route[1]]
		TIME += 1
		# Tick the entities
		for entity in ENTITIES:
			entity.frame()
		checkLight()
	elif route and len(route) == 2:
		move = True
		for entity in ENTITIES:
			if [entity.x, entity.y] == [*route[1]]:
				move = False
				entity.health -= 1
				if INVENTORY_MAINHAND:
					entity.health -= INVENTORY_MAINHAND.getdef()["params"]["damage"]
					TIME += INVENTORY_MAINHAND.getdef()["params"]["speed"]
				else: TIME += 1
			entity.frame()
		if move:
			playerpos = [*route[1]]
			TIME += 1
		else:
			# We're attacking-- don't move
			TARGET = [*playerpos]
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
				TARGET = [x, y]
	# Draw the entities
	for entity in ENTITIES:
		entity.draw(screen, offset)
	# Draw the items
	for i in ITEMS:
		i.draw(screen, offset)
		if [i.x, i.y] == playerpos:
			i.collect()
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
