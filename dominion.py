from enum import Enum
from collections import namedtuple
import random

Card = namedtuple('card', 'name type cost effects vp')

CardType = Enum('CardType', 'treasure victory')

EffectType = Enum('EffectType', 'coins')

Effect = namedtuple('effect', 'type value')

cards = [
    Card('copper', CardType.treasure, 0, [Effect(EffectType.coins, 1)], 0),
    Card('silver', CardType.treasure, 3, [Effect(EffectType.coins, 2)], 0),
    Card('gold', CardType.treasure, 6, [Effect(EffectType.coins, 3)], 0),
    Card('estate', CardType.victory, 2, [], 1),
    Card('duchy', CardType.victory, 5, [], 3),
    Card('province', CardType.victory, 8, [], 6)
]

cardByName = {card.name: card for card in cards}

initialPlayerCards = [cardByName['copper']] * 7 + [cardByName['estate']] * 3

def initialPlayerDeck():
    return random.sample(initialPlayerCards, len(initialPlayerCards))

class PlayerState:
    def __init__(self):
        self.deck = initialPlayerDeck()
        self.hand = []
        self.discard = []
        for _ in range(5):
            self.draw()

    def __repr__(self):
        return 'PlayerState(deck={!r}, hand={!r}, discard={!r})'.format(self.deck, self.hand, self.discard)

    def __str__(self):
        return 'PlayerState(deck size={}, hand={}, discard={})'.format(len(self.deck), self.hand, self.discard)

    def draw(self):
        if not self.deck:
            self.deck = self.discard
            self.discard = []
            random.shuffle(self.deck)
        if self.deck:
            self.hand.append(self.deck.pop())


class GameState:
    def __init__(self, players):
        self.players = {player: PlayerState() for player in players}
        self.supply = {
            'copper': [cardByName['copper']] * 60,
            'silver': [cardByName['silver']] * 40,
            'gold': [cardByName['gold']] * 30,
            'estate': [cardByName['estate']] * 8,
            'duchy': [cardByName['duchy']] * 8,
            'province': [cardByName['province']] * 8,
        }

    def __repr__(self):
        return 'GameState(players={})'.format(self.players)

if __name__ == '__main__':
    gameState = GameState(['mikko', 'beta-ai'])
    print(gameState)
