import os, sys

import pygame
from pygame.locals import *

from math import *
import numpy as np

import random

from die import *

MAIN_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(MAIN_DIR, "img")

SCREENSIZE = 540
FIELDSIZE = 15		# radius of the circle
MEEPLESIZE = 40

BG_COLOR = (194, 194, 163)
PLAYER_COLORS = np.array([
	[255, 0, 0],
	[255, 255, 0],
	[0, 0, 255],
	[0, 255, 0]])

ROLL_DICE = USEREVENT

"""Divide board in 18 parts:
1+1 field padding on the side
11 fields
5 spacing between the fields

Positions of the fields are given as relative coordinates on the board"""

OUT_POS = (SCREENSIZE / 18) * np.array([
	[1, 1],
	[2.5, 1],
	[2.5, 2.5],
	[1, 2.5]])

HOME_POS = (SCREENSIZE / 18) * np.array([
	[3.0, 9],
	[4.5, 9],
	[6.0, 9],
	[7.5, 9]])

FIELDS_POS = (SCREENSIZE / 18) * np.array([
	[1.5, 7.5],
	[3.0, 7.5],
	[4.5, 7.5],
	[6.0, 7.5],
	[7.5, 7.5],
	[7.5, 6.0],
	[7.5, 4.5],
	[7.5, 3.0],
	[7.5, 1.5],
	[9.0, 1.5]])


def load_img(name):
	"""Load an image as surface. Return an image and rect object"""
	path = os.path.join(IMG_DIR, name)
	image = pygame.image.load(path)
	image_rect = image.get_rect()
	return image, image_rect


def rotate(point, origin, angle):
	"""Rotate a point (px, py) around an origin (ox, oy) by an angle.
	Rounds to an integer.
	Used to create the field sprites more easily."""
	ox, oy = origin
	px, py = point

	qx = ox + cos(angle)*(px-ox) - sin(angle)*(py-oy)
	qy = oy + sin(angle)*(px-ox) + cos(angle)*(py-oy)
	return round(qx), round(qy)


def change_color(image, from_color, to_color):
	"""Change the color of an image object. Return the recolored image"""

	width, height = image.get_size()
	for x in range(width):
		for y in range(height):
			if image.get_at((x, y)) == from_color:
				image.set_at((x, y), to_color)
	return image

class S_Mouse(pygame.sprite.Sprite):
	"""create a 'phantom sprite' of the mouse to check collisions"""

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((0, 0))
		self.rect = self.image.get_rect()

	def update(self):
		self.rect.center = pygame.mouse.get_pos()

class S_Field(pygame.sprite.Sprite):
	"""Spite class to create the fields"""

	def __init__(self, pos, radius, color):
		pygame.sprite.Sprite.__init__(self)
		# set up the circle
		img = pygame.Surface((2*radius, 2*radius)).convert()
		img.fill(BG_COLOR)
		pygame.draw.circle(img, color, (radius, radius), radius, 0)
		pygame.draw.circle(img, (0, 0, 0), (radius, radius), radius, 3)
		# set the sprite properties
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.center = pos
		self.radius = radius
		self.occupied = False


class S_Meeple(pygame.sprite.Sprite):
	"""Create a meeple of desired color at desired position"""

	def __init__(self, pos, size, color, grabbed=False):
		pygame.sprite.Sprite.__init__(self)
		# load the meeple image
		img, img_rect = load_img("meeple.png")
		width, height = img.get_size()
		# Change the color and the size and convert it
		img = change_color(img, (0, 0, 0), color)
		img = pygame.transform.scale(img, (size, size))
		img = img.convert_alpha()
		# set the sprite's properties
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.center = pos
		self.grabbed = grabbed

	def update(self):
		if self.grabbed:
			self.rect = self.rect.move(mouse_rel)

	# def move(self):


F_out, F_home, F_board = [], [], []
S_meeples = []


def draw_board():
	"""Creates all the sprites for the fields and the meeples and draws them on the board. """

	for player in range(4):
		F_out.append([])
		F_home.append([])
		S_meeples.append([])

		"""Create the field of a player"""
		position = rotate(FIELDS_POS[0], [SCREENSIZE/2]*2, player*pi/2)
		F_board.append(S_Field(position,
							   FIELDSIZE,
							   0.5*PLAYER_COLORS[player]))
		"""Create the out fields"""
		for field in OUT_POS:
			position = rotate(field, [SCREENSIZE/2]*2, player*pi/2)
			F_out[player].append(S_Field(position,
										 FIELDSIZE,
										 PLAYER_COLORS[player]))
		"""Create the home fields"""
		for field in HOME_POS:
			position = rotate(field, [SCREENSIZE/2]*2, player*pi/2)
			F_home[player].append(S_Field(position,
										  FIELDSIZE,
										  PLAYER_COLORS[player]))
		"""Create the rest of the board fields with white color"""
		for field in FIELDS_POS[1:]:
			position = rotate(field, [SCREENSIZE/2]*2, player*pi/2)
			F_board.append(S_Field(position,
								   FIELDSIZE, 
								   (255, 255, 255)))
		"""Create the meeples and place them in the out fields"""
		for field in OUT_POS:
			position = rotate(field, [SCREENSIZE/2]*2, player*pi/2)
			S_meeples[player].append(S_Meeple(position, 
											  MEEPLESIZE, 
											  PLAYER_COLORS[player]))


"""Initialize the display, board elements and clock"""
pygame.init()
screen = pygame.display.set_mode((SCREENSIZE, SCREENSIZE))
pygame.display.set_caption("Mensch ärgere dich nicht! :)")
background = pygame.Surface(screen.get_size()).convert()
background.fill(BG_COLOR)
screen.blit(background, (0, 0))

draw_board()				# creates all the sprites for fields and meeples
mousesprite = S_Mouse()
die = S_die(ONE, 100, (200, 200))

# Create Sprite groups
SG_Fields = pygame.sprite.Group(F_out, F_home, F_board)
SG_Meeples = pygame.sprite.LayeredUpdates(S_meeples)
Selected_Meeple = pygame.sprite.GroupSingle()
SG_Die = pygame.sprite.GroupSingle(die)
AllSprites = pygame.sprite.Group(SG_Meeples,SG_Die)

# Draw/blit all sprites on the screen
SG_Fields.draw(screen)
SG_Meeples.draw(screen)
SG_Die.draw(screen)

pygame.display.flip()		# update the full display

clock = pygame.time.Clock()

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

				# grab only the top most sprite and make it the top most sprite in the sprite group of all meeples
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
		elif event == ROLL_DICE:
			rnd = random.randint(0, 5)
			die.draw_number(NUMBERS[rnd])


	# Update the mouse and meeple sprites
	mousesprite.update()
	SG_Meeples.update()
	# Draw
	screen.blit(background, (0, 0))
	SG_Fields.draw(screen)
	SG_Meeples.draw(screen)
	SG_Die.draw(screen)

	# Update the full display
	pygame.display.flip()

	clock.tick(120)
