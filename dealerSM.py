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
import client_state_machine as csm
Index
class DealerSM:
        init:
            deck
            pot
            group
            turn
            winner
            round
            game_state
        functions:
            send_card_to_player
            add_card_to_table
            
            
                
class DealerSM(self):
    def __init__(self):
        self.deck = []
        self.pot = 0
        self.group = None
        self.turn = 0
        self.group = 0
        self.
        