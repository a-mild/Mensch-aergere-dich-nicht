import os, sys, ctypes, collections

import pygame
from pygame.locals import *

from math import *
import random

import pandas as pd

from loadstuff import *
from config import *
from objects import *
from init import *

##############################################################################

# print()

# Initialize Players, also creates a spritegroup for the meeples of each player

setup_players = [["P1", True], ["P2", False], ["P3", False], ["P4", True]]

setup = pd.DataFrame(setup_players, columns=["name", "joined_game"])

columns = ["name", "joined_game", "throws_left", 
			"meeplesprites", "meeplegroup", 
			"meeplepos",
			"meeples_out", "meeples_home"]

all_players = pd.DataFrame(columns=columns)
all_players = pd.concat([all_players, setup])

# print(all_players)

"""Initialize the display, board elements and clock"""
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)
pygame.display.set_caption("Mensch ärgere dich nicht! :)")
background = pygame.Surface(screen.get_size()).convert()
background.fill(BG_COLOR)
screen.blit(background, (0, 0))
clock = pygame.time.Clock()

# # Init the spritegroups
# SG_allFields = pygame.sprite.Group()
# SG_allMeeples = pygame.sprite.LayeredUpdates()
# SG_allowedSprites = pygame.sprite.LayeredUpdates()
# SG_allSelected = pygame.sprite.Group()
# SG_die = pygame.sprite.GroupSingle()
# SG_selectedMeeple = pygame.sprite.GroupSingle()
# SG_admissable = pygame.sprite.RenderUpdates()

players = all_players[all_players["joined_game"] == True]

number_players = len(players)

# print(players)

# board = 

# Create the fields
Home = Board.create_home()
Out = Board.create_out()
Fields = Board.create_fields()
SG_allFields.add(Home, Out, Fields)
SG_BoardFields.add(Fields)

# Create Player instances and their meeples
for playerid, row in players.iterrows():
	row["throws_left"] = 3
	row["meeplepos"] = ["O", "O", "O", "O"]
	row["meeples_out"] = 4
	row["meeples_home"] = 0

	meeples = []
	for i in range(4):
		meeples.append(S_Meeple(playerid,
								i,
								MEEPLESIZE))
	print("meeples von spieler {} gebaut!".format(playerid))
	players.loc[playerid]["meeplesprites"] = meeples
	group = pygame.sprite.LayeredUpdates(meeples)
	players.loc[playerid]["meeplegroup"] = group
	SG_allMeeples.add(meeples)

# print(players)

# Create & draw sidebar elements
draw_sidebar(screen)

EventBox = Event_Box(screen)
Die = S_die(EB=EventBox, size=DIESIZE)
SG_die.add(Die)

# Draw/blit all sprites on the screen
SG_allFields.draw(screen)
SG_allMeeples.draw(screen)
SG_die.draw(screen)

pygame.display.flip()		# update the full display

# Choose starting player randomly
active_p = random.choice(list(players.index))

# ~~~~~~~~~~~~~~~~~~~~~~~~~ start the game! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

running = True
while running:
	player = players.loc[active_p]
	print("Spieler {} an der Reihe!".format(player["name"]))
	print("Du darfst noch {} mal würfeln".format(player["throws_left"]))
	# Set which elements the player can click
	add_sprite(_from=[Die, player["meeplesprites"]],
					_to=SG_allowedSprites)

	while player["throws_left"] > 0:
		mouse_pos = pygame.mouse.get_pos()
		mouse_rel = pygame.mouse.get_rel()
		# Exit part
		for event in pygame.event.get():
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				sys.exit()
			elif event.type == QUIT:
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:				# left mouse button
					clickedsprite = find_sprite(SG_allowedSprites, mouse_pos)
					try:
						if clickedsprite is not None:
							if type(sprite) == S_die:
								if not Die.rolling:
									Die.start_roll()
								else:
									Die.stop_roll()
								grabbed_meeple = None
							elif type(sprite) == S_Meeple:
								grabbed_meeple = copy(clickedsprite)
								sprite.grab(SG_allMeeples)
					except:
						print("Hier ist kein klickbarer sprite")
					finally:
						clickedsprite = None
			elif event.type == MOUSEBUTTONUP:
				if (event.button == 1) and grabbed_meeple:
					if grabbed_meeple.drop(grabbed_meeple.save_pos,
									SG_admissable,
									player.name):
						SG_admissable.empty()
						player["throws_left"] -= 0
					else:
						print("Stell den Meeple auf's richtige Feld!")
			elif event.type == ROLL_DIE:
				Die.roll()
			elif event.type == STOP_DIE:
				Die.throw(player)

		# Updates
		SG_allMeeples.update(mouse_rel)

		# Draw
		screen.blit(background, (0, 0))
		screen.blit(EventBox.image, EVENTBOX_POS)
		SG_allFields.draw(screen)
		SG_admissable.draw(screen)
		SG_allMeeples.draw(screen)
		SG_die.draw(screen)

		# Update the full display
		# pygame.display.update(changed_rects)
		pygame.display.flip()

		clock.tick(120)
	# update the start of all players
	for player in players:
		players[2].check_state(number_players)
	# move to next participating player
	active_player = ((active_player + 1) % 4) + 1
	while players[active_player][1] is False:
		active_player += 1

