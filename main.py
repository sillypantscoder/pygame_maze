import pygame
import random
import math

pygame.font.init()

# Colors
BACKGROUND = (0, 0, 0)
TEXTCOLOR = (255, 255, 255)
TILEEMPTY = (200, 200, 200)
TILEWALL = (100, 100, 100)
COINCOLOR = (217, 106, 22)
TILEENDGAME = (0, 120, 68)
PLAYERCOLOR = (0, 0, 0)

# Setup
ZOOM = 50
BOARD = [{"x": x, "y": y, "state": 1 * ((x != 0) and (y != 0))} for x in [-1, 0, 1] for y in [-1, 0, 1]]
FONT = pygame.font.SysFont("monospace", 30)
FONTHEIGHT = FONT.render("0", True, TEXTCOLOR).get_height()
playerpos = [0, 0]
SCREENSIZE = [500, 500 + FONTHEIGHT]
coins = 0
portalroom = False

def getBlock(x: int, y: int) -> "dict[str, int] | None":
	"""Returns the block at the given coordinates."""
	for block in BOARD:
		if block["x"] == x and block["y"] == y:
			return block

def getPlayerBlock() -> "dict[str, int]":
	"""Returns the block the player is on."""
	return getBlock(playerpos[0], playerpos[1])

def playerMove(direction: str) -> None:
	"""Moves the player in the given direction."""
	if direction == "up":
		playerpos[1] -= 1
		if getPlayerBlock()["state"] == 1: playerpos[1] += 1
	elif direction == "down":
		playerpos[1] += 1
		if getPlayerBlock()["state"] == 1: playerpos[1] -= 1
	elif direction == "left":
		playerpos[0] -= 1
		if getPlayerBlock()["state"] == 1: playerpos[0] += 1
	elif direction == "right":
		playerpos[0] += 1
		if getPlayerBlock()["state"] == 1: playerpos[0] -= 1
	# Check the surrounding blocks to make sure they exist.
	if getBlock(playerpos[0]    , playerpos[1]    ) == None: addBlock(playerpos[0]    , playerpos[1]    ) # Player position
	if getBlock(playerpos[0] + 1, playerpos[1]    ) == None: addBlock(playerpos[0] + 1, playerpos[1]    ) # Right
	if getBlock(playerpos[0]    , playerpos[1] + 1) == None: addBlock(playerpos[0]    , playerpos[1] + 1) # Down
	if getBlock(playerpos[0] - 1, playerpos[1]    ) == None: addBlock(playerpos[0] - 1, playerpos[1]    ) # Left
	if getBlock(playerpos[0]    , playerpos[1] - 1) == None: addBlock(playerpos[0]    , playerpos[1] - 1) # Up

def addBlock(x: int, y: int) -> None:
	"""Adds a block to the board."""
	global portalroom
	s = newBlockState(x, y)
	if s == 3: portalroom = True
	BOARD.append({"x": x, "y": y, "state": s})

def newBlockState(x: int, y: int) -> int:
	"""Generates a new block state."""
	if math.dist((x, y), (0, 0)) > 60: return random.choices([1, 2, 3], weights=[1, 25, 5], k=1)[0]
	if math.dist((x, y), (0, 0)) > 10 and not portalroom:
		return random.choices([0, 1, 2, 3], weights=[30, 22, 0.7, 0.1], k=1)[0]
	elif math.dist((x, y), (0, 0)) < 4:
		return random.choices([0, 1, 2], weights=[30, 18, 4], k=1)[0]
	return random.choices([0, 1, 2], weights=[30, 22, 4], k=1)[0]

screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
pygame.key.set_repeat(300, 50)

c = pygame.time.Clock()
running = True
while running:
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
	# Drawing
	offset = [(SCREENSIZE[0] / 2) + (ZOOM / -2) + (playerpos[0] * -ZOOM), (SCREENSIZE[1] / 2) + (ZOOM / -2) + (playerpos[1] * -ZOOM)]
	screen.fill(BACKGROUND)
	for cell in BOARD:
		cellrect = pygame.Rect(cell["x"] * ZOOM, cell["y"] * ZOOM, ZOOM, ZOOM)
		cellrect.move_ip(*offset)
		if cell["state"] == 0:
			pygame.draw.rect(screen, TILEEMPTY, cellrect)
		if cell["state"] == 1:
			pygame.draw.rect(screen, TILEWALL, cellrect)
		if cell["state"] == 2:
			pygame.draw.rect(screen, TILEEMPTY, cellrect)
			pygame.draw.circle(screen, COINCOLOR, cellrect.center, int(ZOOM / 4))
			if cell["x"] == playerpos[0] and cell["y"] == playerpos[1]:
				cell["state"] = 0
				coins += 1
		if cell["state"] == 3:
			pygame.draw.rect(screen, TILEENDGAME, cellrect)
			if cell["x"] == playerpos[0] and cell["y"] == playerpos[1] and coins > 20:
				print("You Win")
				coins -= 20
	playerrect = pygame.Rect((playerpos[0] * ZOOM) + (ZOOM / 3), (playerpos[1] * ZOOM) + (ZOOM / 3), ZOOM / 3, ZOOM / 3)
	playerrect.move_ip(*offset)
	pygame.draw.rect(screen, PLAYERCOLOR, playerrect)
	toolbarrect = pygame.Rect(0, SCREENSIZE[1] - FONTHEIGHT, SCREENSIZE[0], FONTHEIGHT)
	pygame.draw.rect(screen, BACKGROUND, toolbarrect)
	screen.blit(FONT.render("Coins: " + str(coins), True, TEXTCOLOR), toolbarrect.topleft)
	# Flip
	pygame.display.flip()
	c.tick(60)
