import os, sys

import pygame
from pygame.locals import *

from math import *
import numpy as np

import random

from loadstuff import *
from config import *
from objects import *
from init import *

##############################################################################

"""Initialize the display, board elements and clock"""
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)
pygame.display.set_caption("Mensch ärgere dich nicht! :)")
background = pygame.Surface(screen.get_size()).convert()
background.fill(BG_COLOR)
screen.blit(background, (0, 0))
clock = pygame.time.Clock()

# Create the sprites
draw_board()				# create & draw all sprites for fields and meeples
draw_sidebar(screen)		# create & draw the sidebar elements
EventBox = Event_Box(screen)
Die = S_die(EB = EventBox, size=DIESIZE)

mousesprite = S_Mouse()


# Create Sprite groups
SG_Fields = pygame.sprite.Group(F_out, F_home, F_board)
SG_Meeples = pygame.sprite.LayeredUpdates(S_meeples)
Selected_Meeple = pygame.sprite.GroupSingle()
Selected_Sprite = pygame.sprite.Group()
SG_Die = pygame.sprite.GroupSingle(Die)
AllSprites = pygame.sprite.LayeredUpdates((SG_Meeples, SG_Die))

# Draw/blit all sprites on the screen
SG_Fields.draw(screen)
SG_Meeples.draw(screen)
SG_Die.draw(screen)

pygame.display.flip()		# update the full display

print(type(Die) == S_die)
print(type(Die) == objects.S_die)
# print(type(Die) == S_die)



i = 0
# Main loop
running = True
while running:
	mouse_pos = pygame.mouse.get_pos()
	mouse_rel = pygame.mouse.get_rel()
	# Exit part
	for event in pygame.event.get():
		if event.type == KEYDOWN and event.key == K_ESCAPE:	# press ESC to exit
			sys.exit()
		elif event.type == QUIT:
			sys.exit()
		elif event.type == MOUSEBUTTONDOWN:
			if event.button == 1:	# left mouse button
				# grab only the top most sprite 
				Selected_Sprite = AllSprites.get_sprites_at(mouse_pos)[-1]
				if Selected_Sprite.__class__ == S_die:
					if Die.rolling == False:
						Die.start_roll()
					else:
						Die.stop_roll()
				elif Selected_Sprite in SG_Meeples:
					Selected_Meeple = SG_Meeples.get_sprites_at(mouse_pos)[-1]
					if Selected_Meeple:
						SG_Meeples.move_to_front(Selected_Meeple)
						# save the position of the meeple if it wasnt grabbed before so the meeple can get moved back to that position
						if not Selected_Meeple.grabbed:
							save_pos = Selected_Meeple.rect
						Selected_Meeple.grabbed = True
		elif event.type == MOUSEBUTTONUP:
			if event.button == 1 and Selected_Meeple:
				"""Check if the meeple got dropped on a field, if not move back"""
				if pygame.sprite.spritecollide(Selected_Meeple,
											   SG_Fields,
											   False): 
					Selected_Meeple.grabbed = False
					Selected_Meeple.remove
				else:
					Selected_Meeple.rect = save_pos
					Selected_Meeple.grabbed = False
					Selected_Meeple.remove
		elif event.type == ROLL_DIE:
			Die.roll()
		elif event.type == STOP_DIE:
			Die.throw()


	# Update the mouse and meeple sprites
	mousesprite.update()
	SG_Meeples.update(mouse_rel)
	# print(i, SG_Meeples.layers())
	# Draw
	screen.blit(background, (0, 0))			# only over changed rects
	screen.blit(EventBox.image, EVENTBOX_POS)
	SG_Fields.draw(screen)
	SG_Meeples.draw(screen)
	SG_Die.draw(screen)

	# print(changed_rects)
	# Update the full display
	# pygame.display.update(changed_rects)
	pygame.display.flip()

	clock.tick(120)
	i += 1
