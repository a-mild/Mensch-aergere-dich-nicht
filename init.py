import os, sys, copy

import pygame
from pygame.locals import *

from math import *
import numpy as np

import random

from config import *
from loadstuff import *
from objects import *

###############################################################################

pygame.init()




class Board:
	""" Contains the functions to create the parts of the board"""
	def create_out():
		out = []
		for player in range(4):
			"""Create the out fields"""
			out.append([])
			i = 0
			for field in OUT_POS:
				position = rotate(field, [BOARDSIZE/2]*2, player*pi/2)
				out[player].append(S_Field(("O", player, i),
											position,
										 FIELDSIZE,
										 player))
				i += 1
		return out

	def create_home():
		home = []
		for player in range(4):
			"""Create the home fields"""
			home.append([])
			i = 0
			for field in HOME_POS:
				position = rotate(field, [BOARDSIZE/2]*2, player*pi/2)
				home[player].append(S_Field(("H", player, i),
											position,
											FIELDSIZE,
											player))
				i += 1
		return home

	def create_fields():
		"""Create the fields of all players"""
		fields = []
		i = 0
		for player in range(4):
			""" Create the start field with different color"""
			position = rotate(FIELDS_POS[0], [BOARDSIZE/2]*2, player*pi/2)
			fields.append(S_Field((None, None, i),
								  position,
								  FIELDSIZE,
								  color=0.5*PLAYER_COLORS[player]))
			i += 1
			"""Create the rest of the board fields with white color"""
			for field in FIELDS_POS[1:]:
				position = rotate(field, [BOARDSIZE/2]*2, player*pi/2)
				fields.append(S_Field((None, None, i),
									  position,
									  FIELDSIZE))
				i += 1
		return fields

def draw_sidebar(surface):
	sidebar = pygame.Surface(SIDEBARSIZE)
	sidebar.fill(BG_COLOR)
	# draw static elements
	pygame.draw.line(sidebar, BLACK, (0, 0), (0, BOARDSIZE), 4)

	# blit thit shit
	surface.blit(sidebar, SIDEBARPOS)
