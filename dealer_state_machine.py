# -*- coding: utf-8 -*-
"""
Created on Sun May  7 18:29:01 2017

@author: kevinorellana
"""
import time
import socket
import select
import sys
from chat_utils import *
import chat_group
import client_state_machine as csm
import threading 

#HANDLER CODES FROM PLAYERS
PASS = "P"
BET = "B"
#RAISE = "R"
FOLD = "F"
HAND = "H"
READY = "O"

#HANDLER CODES TO PLAYERS
TURN = "T"
CARD = "C"
TABLE_POT = "P"
WINNER = "W"
LOSER = "L"
TABLE_CARDS = "A"
ROUND_STATE = "S"
RANKING = "R"
GAME_STATE = "G"


#==============================================================================
#                            <----- Index ----->
# class DealerSM:
#         __init__:
#             deck
#             pot
#             group
#             player_turn
#             winner
#             round_state
#             game_state
#             socket
#         methods:
#             send_card_to_player
#             add_card_to_table
#             burn_card
#             check_status_of_player
#             check_highest_player_rank
#             get_move_from_player
#==============================================================================
            
        
class DealerSM:
    def __init__(self):
        self.deck = []
        self.pot = 0
        self.players_group = None
        self.player_turn = None
        self.winner = None
        self.round_state
        self.game_state = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
#        STARTING GAME
    def start_game(self):
        for i in self.players_group.members():
            
            
        