import os
import numpy as np
from math import *

from pygame.locals import *

# directions
MAIN_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(MAIN_DIR, "img")

# screen config
BOARDSIZE = 540
SIDEBARSIZE = (200, BOARDSIZE)
SIDEBARPOS = (BOARDSIZE, 0)
SCREENSIZE = (BOARDSIZE + SIDEBARSIZE[0], BOARDSIZE)


# object config
FIELDSIZE = 15		# radius of the circle
MEEPLESIZE = 40

# Die
DIESIZE = 160
DIEPOS = (SIDEBARPOS[0] + 20, SIDEBARPOS[1] + 20)

# Eventbox
EVENTBOX_POS = (BOARDSIZE, BOARDSIZE // 2)
EVENTBOX_SIZE = (200, BOARDSIZE // 2)

FONTSIZE = 20

"""Field relative positions

Divide board in 18 parts:
1+1 field padding on the side
11 fields
5 spacing between the fields

Positions of the fields are given as relative coordinates on the board"""

OUT_POS = (BOARDSIZE / 18) * np.array([
	[1, 1],
	[2.5, 1],
	[2.5, 2.5],
	[1, 2.5]])

HOME_POS = (BOARDSIZE / 18) * np.array([
	[3.0, 9],
	[4.5, 9],
	[6.0, 9],
	[7.5, 9]])

FIELDS_POS = (BOARDSIZE / 18) * np.array([
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

# player config
PLAYER_COLORS = np.array([
	[255, 0, 0],
	[255, 255, 0],
	[0, 0, 255],
	[0, 255, 0]])

# die config
ONE = 1 / 5 * np.array([
	(2.5, 2.5)])
TWO = 1 / 5 * np.array([
	[1.0, 4.0],
	[4.0, 1.0]])
THREE = 1 / 5 * np.array([
	[1.0, 4.0],
	[2.5, 2.5],
	[4.0, 1.0]])
FOUR = 1 / 5 * np.array([
	[1.0, 1.0],
	[1.0, 4.0],
	[4.0, 1.0],
	[4.0, 4.0]])
FIVE = 1 / 5 * np.array([
	[1.0, 1.0],
	[1.0, 4.0],
	[4.0, 1.0],
	[4.0, 4.0],
	[2.5, 2.5]])
SIX = 1 / 5 * np.array([
	[1.0, 1.0],
	[1.0, 2.5],
	[1.0, 4.0],
	[4.0, 1.0],
	[4.0, 2.5],
	[4.0, 4.0]])

NUMBERS = np.array([ONE, TWO, THREE, FOUR, FIVE, SIX])

# Userevents
ROLL_DIE = USEREVENT
STOP_DIE = USEREVENT + 1

# rotate function to hlep create the fields
def rotate(point, origin, angle):
	"""Rotate a point (px, py) around an origin (ox, oy) by an angle.
	Rounds to an integer.
	Used to create the field sprites more easily."""
	ox, oy = origin
	px, py = point

	qx = ox + cos(angle)*(px-ox) - sin(angle)*(py-oy)
	qy = oy + sin(angle)*(px-ox) + cos(angle)*(py-oy)
	return round(qx), round(qy)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0 , 0)
SILVER = (192, 192, 192)
BG_COLOR = (158, 184, 108)



# others
global changed_rects
changed_rects = []			# reset 