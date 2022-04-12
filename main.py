import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ZOOM = 50
BOARD = [{"x": x, "y": y, "state": 1 * ((x != 0) and (y != 0))} for x in [-1, 0, 1] for y in [-1, 0, 1]]
playerpos = [0, 0]
SCREENSIZE = [500, 500]

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
	BOARD.append({"x": x, "y": y, "state": newBlockState()})

def newBlockState() -> int:
	"""Generates a new block state."""
	return random.choices([0, 1], weights=[5, 1], k=1)[0]

screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)

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
			if event.key == pygame.K_w:
				playerMove("up")
			elif event.key == pygame.K_s:
				playerMove("down")
			elif event.key == pygame.K_a:
				playerMove("left")
			elif event.key == pygame.K_d:
				playerMove("right")
	# Drawing
	offset = [(SCREENSIZE[0] / 2) - (ZOOM / 2), (SCREENSIZE[1] / 2) - (ZOOM / 2)]
	screen.fill(WHITE)
	alreadySeen = []
	for cell in BOARD:
		cellrect = pygame.Rect(cell["x"] * ZOOM, cell["y"] * ZOOM, ZOOM, ZOOM)
		cellrect.move_ip(*offset)
		if cell["state"] == 0:
			pygame.draw.rect(screen, BLACK, cellrect, 1)
		if cell["state"] == 1:
			pygame.draw.rect(screen, BLACK, cellrect)
	playerrect = pygame.Rect((playerpos[0] * ZOOM) + (ZOOM / 3), (playerpos[1] * ZOOM) + (ZOOM / 3), ZOOM / 3, ZOOM / 3)
	playerrect.move_ip(*offset)
	pygame.draw.rect(screen, BLACK, playerrect)
	# Flip
	pygame.display.flip()
	c.tick(60)
