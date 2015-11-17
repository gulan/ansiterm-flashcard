#!/usr/bin/env python3

import random

def dealer_pylists(cardset):

    class dealer:
        
        def __init__(self):
            """Parting from the spec, I just use lists for everything."""
            self._dealt = []
            self._play = []
            self._trash = []
            self._kept = cardset[:]
            self.shuffle()
            
        def invarient(self):
            return set(self._dealt) | set(self._play) | set(self._kept) | set(self._trash) == set(cardset)
            
        def shuffle(self):
            assert len(self._dealt) == 0
            n = len(self._kept) // 2
            top = random.shuffle(self._kept[:n])
            bot = random.shuffle(self._kept[n:])
            self._play = top + bot + self._play
            self._kept = []
            
        def toss(self):
            (answer, question, b) = self._dealt.pop()
            assert not b
            self._trash.append((answer, question))
            self._dealt = []
            
        def keep(self):
            (answer, question, b) = self._dealt.pop()
            assert not b
            self._kept.append((answer, question))
            self._dealt = []
            
        def deal(self):
            assert self._dealt == []
            assert len(self._play) > 0
            (answer, question) = self._play[0]
            new_card = (answer, question, True)
            self._dealt = [new_card]
            self._play  = self._play[1:]
            return new_card
            
        def flip(self):
            (answer, question, b) = self._dealt.pop()
            assert b
            new_card = (answer, question, False)
            self._dealt = [new_card]
            return new_card
            
        def gameover(self):
            return (len(self._dealt + self._play + self._kept) == 0 
                    and set(cardset) == set(self._trash))
