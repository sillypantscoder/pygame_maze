import pygame
import threading
import random
import boardgen

pygame.font.init()

# Colors
BACKGROUND = (0, 0, 0)
TEXTCOLOR = (255, 255, 255)
TILEEMPTY = (30, 30, 200)
TILEWALL = (255, 40, 40)
TILEDOOR = (217, 106, 22)
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
coins = 0
portalroom = False

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
	wallblocks = [0, 2]
	if direction == "up" and playerpos[1] > 0:
		playerpos[1] -= 1
		if getPlayerBlock()["state"] in wallblocks: playerpos[1] += 1
	elif direction == "down" and playerpos[1] < len(BOARD) - 1:
		playerpos[1] += 1
		if getPlayerBlock()["state"] in wallblocks: playerpos[1] -= 1
	elif direction == "left" and playerpos[0] > 0:
		playerpos[0] -= 1
		if getPlayerBlock()["state"] in wallblocks: playerpos[0] += 1
	elif direction == "right" and playerpos[0] < len(BOARD[0]) - 1:
		playerpos[0] += 1
		if getPlayerBlock()["state"] in wallblocks: playerpos[0] -= 1

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

def asyncLight():
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
					if b["state"] not in [0, 1]:
						walls += 1
			# 4. If there are no walls, set the block to light.
			block["light"] = walls == 0
def asyncMultipleLight():
	global running
	while running:
		asyncLight()
		pygame.time.wait(100)

def pathfind(x, y):
	"""Finds the path from the player to the given block."""
	from pathfinding.core.diagonal_movement import DiagonalMovement
	from pathfinding.core.grid import Grid
	from pathfinding.finder.a_star import AStarFinder
	matrix = [[(state == 0) * 1 for state in row] for row in BOARD]
	for row in matrix:
		print(row)

screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
pygame.key.set_repeat(300, 50)

c = pygame.time.Clock()
running = True
threading.Thread(target=asyncMultipleLight, name="game light daemon", args=()).start()
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
		elif event.type == pygame.MOUSEBUTTONDOWN:
			# Get cell coordinates
			x = int(event.pos[0] / ZOOM)
			y = int(event.pos[1] / ZOOM)
			# Pathfind to the block
			pathfind(x, y)
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
			if cell["state"] == 0:
				# Random white pixel
				pixel_x = random.randint(0, ZOOM - 1)
				pixel_y = random.randint(0, ZOOM - 1)
				screen.set_at((cellrect.left + pixel_x, cellrect.top + pixel_y), TEXTCOLOR)
			elif cell["state"] == 1:
				pygame.draw.rect(screen, TILEEMPTY, cellrect)
			elif cell["state"] == 2:
				pygame.draw.rect(screen, TILEWALL, cellrect)
			elif cell["state"] == 3:
				pygame.draw.rect(screen, TILEEMPTY, cellrect)
				pygame.draw.rect(screen, TILEDOOR, cellrect, ZOOM//10 if player_on else 0)
			else:
				pygame.draw.rect(screen, TILEEMPTY, cellrect)
				o = (cellrect.width / 2, cellrect.height / 2)
				pygame.draw.rect(screen, TILEWALL, pygame.Rect(cellrect.left, cellrect.top, *o))
				pygame.draw.rect(screen, TILEWALL, pygame.Rect(cellrect.left + o[0], cellrect.top + o[0], *o))
			if cell["light"] == False:
				# Dim the cell.
				s = pygame.Surface(cellrect.size, pygame.SRCALPHA)
				s.fill((0, 0, 0, 200))
				screen.blit(s, cellrect)
	playerrect = pygame.Rect((playerpos[0] * ZOOM) + (ZOOM / 3), (playerpos[1] * ZOOM) + (ZOOM / 3), ZOOM / 3, ZOOM / 3)
	playerrect.move_ip(*offset)
	pygame.draw.rect(screen, PLAYERCOLOR, playerrect)
	toolbarrect = pygame.Rect(0, SCREENSIZE[1] - FONTHEIGHT, SCREENSIZE[0], FONTHEIGHT)
	pygame.draw.rect(screen, BACKGROUND, toolbarrect)
	screen.blit(FONT.render("Coins: " + str(coins), True, TEXTCOLOR), toolbarrect.topleft)
	# Flip
	pygame.display.flip()
	c.tick(60)
