import pygame
import random

pygame.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
ORANGE = (217, 106, 22)
ZOOM = 50
BOARD = [{"x": x, "y": y, "state": 1 * ((x != 0) and (y != 0))} for x in [-1, 0, 1] for y in [-1, 0, 1]]
FONT = pygame.font.SysFont("monospace", 30)
FONTHEIGHT = FONT.render("0", True, BLACK).get_height()
playerpos = [0, 0]
SCREENSIZE = [500, 500 + FONTHEIGHT]
coins = 0

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
	return random.choices([0, 1, 2], weights=[30, 20, 2], k=1)[0]

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
	screen.fill(WHITE)
	for cell in BOARD:
		cellrect = pygame.Rect(cell["x"] * ZOOM, cell["y"] * ZOOM, ZOOM, ZOOM)
		cellrect.move_ip(*offset)
		if cell["state"] == 0:
			pygame.draw.rect(screen, GRAY, cellrect)
		if cell["state"] == 1:
			pygame.draw.rect(screen, BLACK, cellrect)
		if cell["state"] == 2:
			pygame.draw.rect(screen, GRAY, cellrect)
			pygame.draw.circle(screen, ORANGE, cellrect.center, int(ZOOM / 4))
			if cell["x"] == playerpos[0] and cell["y"] == playerpos[1]:
				cell["state"] = 0
				coins += 1
	playerrect = pygame.Rect((playerpos[0] * ZOOM) + (ZOOM / 3), (playerpos[1] * ZOOM) + (ZOOM / 3), ZOOM / 3, ZOOM / 3)
	playerrect.move_ip(*offset)
	pygame.draw.rect(screen, BLACK, playerrect)
	toolbarrect = pygame.Rect(0, SCREENSIZE[1] - FONTHEIGHT, SCREENSIZE[0], FONTHEIGHT)
	pygame.draw.rect(screen, WHITE, toolbarrect)
	screen.blit(FONT.render("Coins: " + str(coins), True, BLACK), toolbarrect.topleft)
	# Flip
	pygame.display.flip()
	c.tick(60)
