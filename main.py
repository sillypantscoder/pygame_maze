import pygame

WHITE = (255, 255, 255)

SCREENSIZE = [800, 600]
SCREEN = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)

running = True
c = pygame.time.Clock()
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.VIDEORESIZE:
			SCREENSIZE = event.size
			SCREEN = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
	SCREEN.fill(WHITE)
	pygame.display.flip()
	c.tick(60)