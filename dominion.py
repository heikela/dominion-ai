from enum import Enum
from collections import namedtuple
import random

from choice import Choice
from observation import Observation

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

card_by_name = {card.name: card for card in cards}

initial_player_cards = (
    [card_by_name['copper']] * 7
    + [card_by_name['estate']] * 3)

GameStep = Enum('GameStep', 'action buy cleanup')

ChoiceType = Enum('ChoiceType', 'buy play end_turn')


def initial_player_deck():
    return random.sample(initial_player_cards, len(initial_player_cards))


class PlayerState:
    def __init__(self, name, observation_buffer):
        self._name = name
        self._observations = observation_buffer
        self._deck = initial_player_deck()
        self._hand = []
        self._played = []
        self._discard = []
        self._draw_hand()
        self.start_turn()

    def get_name(self):
        return self._name

    def get_available_spend(self):
        return self._to_spend

    def get_hand(self):
        return self._hand

    def get_buys(self):
        return self._buys

    def draw(self):
        if not self._deck:
            self._deck = self._discard
            self._discard = []
            random.shuffle(self._deck)
        if self._deck:
            drawn_card = self._deck.pop()
            self._hand.append(drawn_card)
            self._draw_card_observed(drawn_card)

    def cleanup(self):
        self._discard_hand()
        self._discard_played()
        self._draw_hand()

    def start_turn(self):
        self._to_spend = 0
        self._buys = 1

    def buy(self, card):
        assert self._to_spend >= card.cost, (
            "Bought a card that cannot be afforded.")
        assert self._buys >= 0, "Bought a card when no buys left"
        self._to_spend -= card.cost
        self._buys -= 1
        self._buy_card_observed(card)
        self.gain(card)

    def play(self, card_name):
        # this should always find a card.
        # Crash with uncaught StopIteration exception if not
        card = next(card for card in self._hand if card.name == card_name)
        self._hand.remove(card)
        self._played.append(card)
        self._play_card_observed(card)
        for effect in card.effects:
            if effect.type == EffectType.coins:
                self._to_spend += effect.value

    def gain(self, card):
        self._discard.append(card)

    def _draw_hand(self):
        for _ in range(5):
            self.draw()

    def _discard_hand(self):
        self._discard.extend(self._hand)
        self._hand = []

    def _discard_played(self):
        self._discard.extend(self._played)
        self._played = []

    def _observation(self, observation):
        self._observations.append(observation)

    def _play_card_observed(self, card):
        message = "{} plays {}".format(self._name, card.name)
        self._observation(Observation(self._name, message, message))

    def _buy_card_observed(self, card):
        message = "{} buys {}".format(self._name, card.name)
        self._observation(Observation(self._name, message, message))

    def _draw_card_observed(self, card):
        private = "{} draws {}".format(self._name, card.name)
        public = "{} draws a card".format(self._name)
        self._observation(Observation(self._name, private, public))


class GameState:
    def __init__(self, players):
        self._observations = []
        self._published_observations = 0
        self._players = [PlayerState(player, self._observations)
                         for player in players]
        self._supply = {
            'copper': [card_by_name['copper']] * 60,
            'silver': [card_by_name['silver']] * 40,
            'gold': [card_by_name['gold']] * 30,
            'estate': [card_by_name['estate']] * 8,
            'duchy': [card_by_name['duchy']] * 8,
            'province': [card_by_name['province']] * 8,
        }
        self._game_step = GameStep.action
        self._active_player_idx = 0

    def get_first_choice(self):
        return (self._publish_observations(),
                self._purchase_or_play_treasure_choice(self._active_player()))

    def get_next_choice(self, chosen):
        choice_type = chosen[0]
        if choice_type == ChoiceType.buy:
            self._purchase(self._active_player(), chosen[1])
            if self._active_player().get_buys() == 0:
                self._cleanup_and_next_player()
        elif choice_type == ChoiceType.play:
            self._active_player().play(chosen[1])
        else:
            self._cleanup_and_next_player()
        return (self._publish_observations(),
                self._purchase_or_play_treasure_choice(self._active_player()))

    def is_game_over(self):
        return False  # todo

    def _publish_observations(self):
        new_observations = self._observations[self._published_observations:]
        self._published_observations = len(self._observations)
        return new_observations

    def _active_player(self):
        return self._players[self._active_player_idx]

    def _cards_available_at(self, cost):
        return [supplyDeck[0]
                for supplyDeck
                in self._supply.values()
                if supplyDeck and supplyDeck[0].cost <= cost]

    def _purchase_or_play_treasure_choice(self, player):
        return Choice(
            player.get_name(),
            list({(ChoiceType.play, card.name)
                  for card in player.get_hand()
                  if card.type == CardType.treasure})
            + [(ChoiceType.buy, card.name)
               for card
               in self._cards_available_at(player.get_available_spend())]
            + [(ChoiceType.end_turn,)])

    def _purchase(self, player, card_name):
        supply_deck = self._supply[card_name]
        assert supply_deck, (
            "Purchase from an empty supply deck should not be possible")
        card = supply_deck.pop()
        player.buy(card)

    def _cleanup_and_next_player(self):
        self._active_player().cleanup()
        self._next_player()

    def _next_player(self):
        self._active_player_idx += 1
        if self._active_player_idx >= len(self._players):
            self._active_player_idx = 0
        self._active_player().start_turn()
