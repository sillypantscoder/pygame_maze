import pygame
import random
import boardgen

WHITE = (255, 255, 255)
screensize = [500, 500]
screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)

cellsize = 10
boardsize = [60, 60]
BOARD = [
	[boardgen.board[i][j] for i in range(boardsize[0])]
		for j in range(boardsize[1])
]

def draw(t, rect):
	if t == "air":
		pygame.draw.rect(screen, WHITE, rect)
	elif t == "stuff":
		pygame.draw.rect(screen, (0, 0, 0), rect)
	else:
		raise Exception(f"Dunno what {t} is, something's wrong :/")

def MAIN():
	global screen
	running = True
	c = pygame.time.Clock()
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.VIDEORESIZE:
				screensize = event.size
				screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
		screen.fill(WHITE)
		# Board
		for i in range(boardsize[0]):
			for j in range(boardsize[1]):
				draw(BOARD[i][j], pygame.Rect(i * cellsize, j * cellsize, cellsize, cellsize))
		# Flip
		pygame.display.flip()
		c.tick(60)

MAIN()