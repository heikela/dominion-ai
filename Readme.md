# Playground for AI for Dominion

*and potentially for other games*

## The premise

Ultimately I am interested in trying to define board game rules
declaratively, and creating game-AIs to play these games.

I am starting with an extremely simplified version of Dominion, and simple control methods,
but I am modelling the game as decisions an agent has to make with
observations delivered in between decisions.

This formulation (which ends up resembling a text adventure no matter what
the original game is), allows for hidden information, randomness, any number of players,
and dependencies across different points in time, but doesn't make any of
this particularly easy to learn for a learning system. For example, in Dominion
I am planning to leave it for the AI to learn that the cards you buy have something to do
with the cards you get to play later or that playing treasures is better than just
ending a turn straight away, or buying something cheap without playing all treasures.

Dominion presents many questions that can be investigated, such as:
- [ ] Is it possible to get an AI to generalise from unseen cards to seen cards.
  - [ ] How is this affected by how cards are presented, e.g. whether card
        abilities are communicated in-line whenever a card is mentioned in
        observations or actions, or only mentioned in rules or left implicit.
- [ ] How do different kingdom cards affect learning results
- [ ] How do different policy evaluation and control methods perform
- [ ] How do different ways to turn observations into a state for
      a function approximator (e.g. for approximating the state action Value
      function Q) affect learning results

For a log of lessons learned, assumptions and observations, see [Findings](findings.md)
