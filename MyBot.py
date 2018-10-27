#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")

explore = {}

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    if game.turn_number == 1:
        shipyardPos = game_map[me.shipyard].position

    futurePos = []

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        if ship.is_full:
            explore[ship.id] = False
        if ship.position == shipyardPos:
            explore[ship.id] = True

        if explore[ship.id]:
            if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:

                while True:
                    direction = random.choice([Direction.West, Direction.North, Direction.East, Direction.South])
                    candidatePos = ship.position.directional_offset(direction)

                    if (candidatePos not in futurePos) and game_map[candidatePos].is_empty:
                        futurePos.append(candidatePos)
                        game_map[candidatePos].mark_unsafe(ship)
                        break

                command_queue.append(ship.move(direction))
            else:
                command_queue.append(ship.stay_still())
                futurePos.append(ship.position)
                game_map[ship.position].mark_unsafe(ship)
        else:
            direction = game_map.naive_navigate(ship, me.shipyard.position)
            candidatePos = ship.position.directional_offset(direction)
            if candidatePos in futurePos:
                command_queue.append(ship.stay_still())
                futurePos.append(ship.position)
                game_map[ship.position].mark_unsafe(ship)
            else:
                command_queue.append(ship.move(direction))
                futurePos.append(candidatePos)
                game_map[candidatePos].mark_unsafe(ship)

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if game.turn_number <= 175 and me.halite_amount >= constants.SHIP_COST and not game_map[
        me.shipyard].is_occupied:  # 00 and game.turn_number % 10 == 0
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
