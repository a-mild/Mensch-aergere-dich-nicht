import os, sys

import pygame
from pygame.locals import *

from math import *
import numpy as np

MAIN_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(MAIN_DIR, "img")

SCREENSIZE = (540, 540)
FIELDSIZE = 15

BG_COLOR = (194, 194, 163)
PLAYER_COLORS = np.array([
	[255, 0, 0],
	[255, 255, 0],
	[0, 0, 255],
	[0, 255, 0]])

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
	[9, 1.5]])


def load_img(name):
	"""Load an image as surface. Return an image and rect object"""
	path = os.path.join(IMG_DIR, name)
	image = pygame.image.load(path).convert()
	image_rect = image.get_rect()
	return image, image_rect


def rotate2D(origin, point, angle):
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
	"""create a 'phantom sprite' for the mouse to check collisions"""

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
		self.image = pygame.Surface((2*radius, 2*radius))
		self.image.fill(BG_COLOR)
		self.rect = self.image.get_rect()
		self.rect.center = pos
		self.radius = radius

		pygame.draw.circle(self.image, color, (radius, radius), radius, 0)


class S_Meeple(pygame.sprite.Sprite):
	"""Create a meeple of desired color at desired position"""

	def __init__(self, pos, SCREENSIZE, color, grabbed=False):
		pygame.sprite.Sprite.__init__(self)
		image, image_rect = load_img("meeple.png")
		width, height = image.get_SCREENSIZE()
		image = change_color(image, (0, 0, 0), color)
		self.image = pygame.transform.scale(image, (SCREENSIZE, SCREENSIZE))
		self.rect = self.image.get_rect()
		self.rect.center = pos
		self.grabbed = grabbed

	def update(self):
		if self.grabbed:
			self.rect = self.rect.move(mouse_rel)



class Board((), 540):
	def __init__(self):
		# Initiliaze mouse sprite
		self.s_mouse = S_Mouse()

		self.f_out, self.f_home, self.f_board = [], [], []
		self.s_meeples = []

		"""Draw all the fields"""
		for player in range(4):
			i = 0
			self.f_out.append([])
			self.f_home.append([])
			self.s_meeples.append([])
			S_startPos = rotate2D([SCREENSIZE/2]*2, FIELDS_POS[0], player*pi/2)
			self.f_board.append(S_Field(S_startPos,
										FIELDSIZE,
										0.5*PLAYER_COLORS[player]))
			for field in OUT_POS:
				position = rotate2D([SCREENSIZE/2]*2, field, player*pi/2)
				self.f_out[player].append(S_Field(position,
												  FIELDSIZE,
												  PLAYER_COLORS[player]))
				i += 1
			for field in HOME_POS:
				position = rotate2D([SCREENSIZE/2]*2, field, player*pi/2)
				self.f_home[player].append(S_Field(position,
												   FIELDSIZE,
												   PLAYER_COLORS[player]))
				i += 1
			for field in FIELDS_POS[1:]:
				position = rotate2D([SCREENSIZE/2]*2, field, player*pi/2)
				self.f_board.append(S_Field(position, FIELDSIZE, (255, 255, 255)))
				i += 1
			"""Draw some meeples"""
			for field in OUT_POS:
				position = rotate2D([SCREENSIZE/2]*2, field, player*pi/2)
				self.s_meeples[player].append(S_Meeple(position, 
													 40, 
													 PLAYER_COLORS[player]))


# Initialize the display, board elements and clock
screen = pygame.display.set_mode(SCREENSIZE)
background = pygame.Surface(SCREENSIZE).convert_alpha()
background.fill(BG_COLOR)
screen.blit(background, (0, 0))

board = Board()
pygame.display.flip()	# update the full display

clock = pygame.time.Clock()

# Create Sprite groups
S_Fields = pygame.sprite.Group(board.f_out,
							   board.f_home,
							   board.f_board)
S_Meeples = pygame.sprite.Group(board.s_meeples)
S_Mouse = pygame.sprite.Group(board.s_mouse)

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
				grabbed_meeple = pygame.sprite.spritecollideany(board.s_mouse, 
															 S_Meeples,
															 False)
				if grabbed_meeple:
					grabbed_meeple.grabbed = not grabbed_meeple.grabbed
		elif event.type == MOUSEBUTTONUP:
			if event.button == 1 and grabbed_meeple:
				grabbed_meeple.grabbed = False

	# Update and draw the field sprites
	S_Meeples.update()
	S_Mouse.update()
	screen.blit(board.background, (0, 0))
	S_Fields.draw(screen)
	S_Meeples.draw(screen)
	S_Mouse.draw(screen)

	pygame.display.flip()  # Update the full display


	clock.tick(120)
