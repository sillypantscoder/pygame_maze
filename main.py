import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ZOOM = 50
BOARD = [{"x": x, "y": y, "state": 1 * ((x != 0) and (y != 0))} for x in [-1, 0, 1] for y in [-1, 0, 1]]
playerpos = [0, 0]
SCREENSIZE = [500, 500]

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
