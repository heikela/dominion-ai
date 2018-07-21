from enum import Enum
from collections import namedtuple
import random

Card = namedtuple('card', 'name type cost effects vp')

CardType = Enum('CardType', 'treasure victory')

EffectType = Enum('EffectType', 'coins')

Effect = namedtuple('effect', 'type value')

cards = [
    Card('copper', CardType.treasure, 0, [Effect(EffectType.coins, 1)], 0),
    Card('silver', CardType.treasure, 3, [Effect(EffectType.coins, 1)], 0),
    Card('gold', CardType.treasure, 6, [Effect(EffectType.coins, 1)], 0),
    Card('estate', CardType.victory, 2, [], 1),
    Card('county', CardType.victory, 5, [], 3),
    Card('province', CardType.victory, 8, [], 6)
]

cardByName = {card.name: card for card in cards}

initialPlayerCards = [cardByName['copper']] * 7 + [cardByName['estate']] * 3

def initialPlayerDeck():
    return random.sample(initialPlayerCards, len(initialPlayerCards))

class GameState:
    def __init__(self, players):
        self.players = {player: {'deck': initialPlayerDeck()} for player in players}

if __name__ == '__main__':
    gameState = GameState(['mikko', 'beta-ai'])
    print(gameState.players)
