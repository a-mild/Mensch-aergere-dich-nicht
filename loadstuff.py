import os
import pygame.image
from pygame.locals import *

from config import *

pygame.init()

def load_img(name):
	"""Load an image as surface and convert it. 
	Return an image and rect object"""
	path = os.path.join(IMG_DIR, name)
	image = pygame.image.load(path)
	if image.get_alpha is None:
		image = image.convert()
	else:
		image = image.convert_alpha()
	image_rect = image.get_rect()
	return image, image_rect

def change_color(image, from_color, to_color):
	"""Change the color of an image object. Return the recolored image"""

	width, height = image.get_size()
	for x in range(width):
		for y in range(height):
			if image.get_at((x, y)) == from_color:
				image.set_at((x, y), to_color)
	return image