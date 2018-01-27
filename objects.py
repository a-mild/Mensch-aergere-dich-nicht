import os, sys

import pygame
from pygame.locals import *

from math import *
import numpy as np

import random

from config import *
from loadstuff import *

##############################################################################

# Init the spritegroups
SG_allFields = pygame.sprite.Group()
SG_BoardFields = pygame.sprite.Group()
SG_allMeeples = pygame.sprite.LayeredUpdates()
SG_allowedSprites = pygame.sprite.LayeredUpdates()
SG_allSelected = pygame.sprite.Group()
SG_die = pygame.sprite.GroupSingle()
SG_selectedMeeple = pygame.sprite.GroupSingle()
SG_admissable = pygame.sprite.RenderUpdates()

#~~~~~~~~~~~~~~~~~~~~~~~~~ general functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def add_sprite(_from, _to):
	try:
		for sprite in _from:
			_to.add(sprite)
	except:
		try:
			_to.add(_from)
		except:
			print("klappt auch net")

def find_sprite(in_group, pos):
	""" find all sprites at pos and return the topmost"""
	try:
		found_sprite = in_group.get_sprites_at(pos)[-1]
		if not (type(found_sprite) == pygame.sprite.GroupSingle): 
			return found_sprite
		else:
			return found_sprite.sprite
	except:
		return None


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Player:
	def __init__(self, id):
		self.turn = False
		# self.id = id
		# self.meeples = self.create_meeples(self.id)
		self.SG_meeples = pygame.sprite.LayeredUpdates(self.meeples)
		self.meeples_out = 4
		self.meeples_home = 0
		self.number_throws = 3

	def create_meeples(self, playerid):
		"""Create the meeples and place them in the out fields"""
		meeples = []
		for meepleid in range(4):
			meeples.append(S_Meeple(playerid,
									meepleid,
									MEEPLESIZE))
		print("meeples von spieler {} gebaut!".format(playerid))
		return meeples

	def set_admissable(self, number):
		allowedFields = []
		if (self.meeples_out == 4) & (number ==6):
				print("Geh auf's Startfeld!")
				goto = SG_BoardFields.sprites()[self.id*10]
				goto.admissable = True
				SG_admissable.add(goto)
				SG_allowedSprites.add(goto)
				print(goto.id)

		else:
			for meeple in self.SG_meeples:
				continue
				# allowedFields.append(meeple.)

	def check_state(self, number_players):
		if self.meeples_home == 4:
			number_players -= 1
			print("Du hast gewonnen!")
		if self.meeples_out == 4:
			self.number_throws = 3
		else:
			self.number_throws = 1


class Event_Box:
	"""Textbox that prints all actions in the game """
	def __init__(self, surface):
		self.image = pygame.Surface(EVENTBOX_SIZE).convert()
		self.image.fill(BG_COLOR)
		self.rect = self.image.get_rect()
		# draw a line around it
		pygame.draw.lines(
			self.image, 
			BLACK,
			True,
			[self.rect.topleft, self.rect.bottomleft, self.rect.bottomright, self.rect.topright],
			5)
		surface.blit(self.image, EVENTBOX_POS)
		# Font setup
		self.font = pygame.font.Font(None, FONTSIZE)
		welcometext = 'Herzlich Willkommen!'
		self.all_lines = []
		self.add_line(welcometext)

	def add_line(self, text):
		"""Add a new line of text to the bottom of the event box"""
		width, height = self.font.size(text)
		pos = (self.rect.left + 10, self.rect.bottom - height- 5)
		rend = self.font.render(text, True, BLACK)
		# Move all already existing lines up
		for i in range(len(self.all_lines)):
			oldsurf, oldpos = self.all_lines[i]
			self.all_lines[i] = self.lift_line(oldsurf, height, oldpos)
			copy = oldsurf.copy()
			copy.fill(BG_COLOR)
			self.image.blit(copy, oldpos)
		self.all_lines.append([rend, pos])
		self.image.blit(rend, pos)

	def lift_line(self, line, height, oldpos):
		newpos = (oldpos[0],  oldpos[1] - height)
		self.image.blit(line, newpos)
		return line, newpos

	def clear_all(self):
		pass

class S_Mouse(pygame.sprite.Sprite):
	"""create a 'phantom sprite' of the mouse to check collisions"""

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((0, 0))
		self.rect = self.image.get_rect()

	def update(self):
		self.rect.center = pygame.mouse.get_pos()


class S_Field(pygame.sprite.Sprite):
	"""Spite class to create the fields
	Key for the field_id = (a, b, c):
	a: H = home, O = out, board field = None
	b: player-id or None if board field
	c: field number """

	def __init__(self, field_id, pos, radius, color=None):
		pygame.sprite.Sprite.__init__(self)
		if field_id[0] is not None:
			if field_id[0] == "H":
				self.type = "home"
			elif field_id[0] == "O":
				self.type = "out"
			self.player = field_id[1]
			self.occupied_by = self.player
			self.color = PLAYER_COLORS[self.player]
		else:
			self.type = "field"
			self.occupied_by = None
			if color is not None:
				self.color = color
			else:
				self.color = WHITE
		self.id = field_id[2]
		self.radius = radius
		self.admissable = False

		# set the sprite properties
		self.image = self.draw_field(self.color)
		self.rect = self.image.get_rect()
		self.rect.center = pos

	def update(self):
		if self.admissable == True:
			self.image = self.draw_field(SILVER)
		else:
			self.image = self.draw_field(self.color)

	def draw_field(self, color):
		img = pygame.Surface((2*self.radius, 2*self.radius)).convert()
		img.fill(BG_COLOR)
		pygame.draw.circle(img,
						   color,
						   (self.radius, self.radius),
						   self.radius,
						   0)
		pygame.draw.circle(img,
						   BLACK,
						   (self.radius, self.radius),
						   self.radius,
						   3)
		return img

class S_Meeple(pygame.sprite.Sprite):
	"""Create a meeple of desired color at desired position"""

	def __init__(self, playerid, meepleid, size):
		pygame.sprite.Sprite.__init__(self)
		self.player = playerid
		self.id = meepleid
		self.grabbed = False

		# set the sprite's properties
		img, img_rect = load_img("meeple.png")
		width, height = img_rect.w, img_rect.h
		img = change_color(img, 
						   (0, 0, 0), 
						   PLAYER_COLORS[self.player])
		img = pygame.transform.scale(img, (size, size))
		self.image = img
		self.rect = self.image.get_rect()
		pos = rotate(OUT_POS[self.id], [BOARDSIZE/2]*2, self.player*pi/2)
		self.rect.center = pos
		self.on_field = ("O", self.player, self.id)

	def update(self, move):
		if self.grabbed:
			self.rect = self.rect.move(move)

	def check_field(self, spritegroup):
		""" Check if the meeple stands on a field, return the field's id"""
		field = pygame.sprite.spritecollideany(self, spritegroup)
		if field:
			return field.id

	def grab(self, meeplegroup):
		"""Grabs the meeple and saves the position where it was grabbed"""
		meeplegroup.move_to_front(self)
		if not self.grabbed:
			self.save_pos = self.rect
		self.grabbed = True
		print("Grabbed meeple {} from player {}".format(self.id, self.player))

	def drop(self, oldpos, fieldgroup, currentplayer):
		""" Drop the meeple on a field. Move back to where it got grabbed if it's not dropped on a field"""
		try:
			dropped_on = pygame.sprite.spritecollide(self,
									   fieldgroup,
									   False)[0]
			if dropped_on.type == "home":
				currentplayer["meeples_home"] += 1
			elif dropped_on.id == currentplayer.id*10:
				currentplayer.meeples_out -= 1
			self.grabbed = False

			return True
		except:
			self.rect = oldpos
			self.grabbed = False
			return False

class S_die(pygame.sprite.Sprite):
	"""Sprite for the die"""
	global EventBox

	def __init__(self, size, EB):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((size, size)).convert()
		self.rect = self.image.get_rect()
		self.rect.topleft = DIEPOS
		self.number = random.randint(1, 6)
		self.size = size
		self.image = self.draw_number(self.number)
		self.roll_speed = 250		# how fast the die shows a new number [ms]
		self.rolling = False

		self.EB = EB

	def update(self):
		pass

	def draw_number(self, number):
		"""Draw a number and return the image object.
		"""
		global changed_rects

		number = number -1		# correct to correct index
		self.image.fill((255, 255, 255))
		pygame.draw.lines(
			self.image,
			(0, 0, 0),		# black
			True,			# connects last to first point
			[(0, 0), (self.size, 0), (self.size, self.size), (0, self.size)],
			self.size//20)			# line width
		for pip in NUMBERS[number]:
			pygame.draw.circle(
				self.image,
				(0, 0, 0),
				(self.size*pip).astype(int),
				self.size//10)					# radius
		# Add the rect to the changed rects list (doesnt work on init)
		changed_rects.append(self.rect)

		return self.image

	def start_roll(self):
		""" Set a timer in the event queu to make the die show a new number every 250 milliseconds"""
		print("Die started!")
		self.rolling = True
		pygame.time.set_timer(ROLL_DIE, self.roll_speed)

	def roll(self):
		"""rolls for a random number and draws the new number"""
		rnd = random.randint(1, 6)
		self.draw_number(rnd)
		return rnd

	def stop_roll(self):
		""" Stops the event queu timer for the rolling animation and starts a new event to slow down the roll speed"""
		print("Die stopped!")
		pygame.time.set_timer(ROLL_DIE, 0)
		pygame.time.set_timer(STOP_DIE, self.roll_speed)

	# @classmethod
	def throw(self, currentplayer):
		""" Called when the die is clicked again while rolling.
		Lets the roll_speed slow down and set the number when it the rolling has stopped"""
		if self.roll_speed < 2000:
			self.roll()
			pygame.time.set_timer(STOP_DIE, self.roll_speed)
			self.roll_speed = round(self.roll_speed**1.53)
		else:
			# Die is still. Call roll one last time and set the number
			print("die is still")
			self.number = self.roll()
			self.rolling = False
			self.roll_speed = 250
			# geht das nicht anders?!
			printline = getattr(self.EB, "add_line")
			printline("Du hast eine {} gewürfelt!".format(str(self.number)))
			pygame.time.set_timer(STOP_DIE, 0)
			# Set the admissable fields
			if self.number == 6:
				if currentplayer["meeples_out"] == 4:
					currentplayer.set_admissable(self.number)
				else:
					currentplayer.set_admissable(self.number)
					currentplayer.number_throws += 1
					print("Extrawurf bekommen!")
			else:				# no 6
				if currentplayer.meeples_out == 4:
					currentplayer.number_throws -= 1	# one less try
					print("Du darfst noch {} mal würfeln".format(
						currentplayer.number_throws))
				currentplayer.set_admissable(self.number)



