'''
2-4 player game of war. 2 players - 26 cards each, 3 - 17, 4 - 13.
It should have optional names arg and arg for number of players. Or
it should count the number of players by the number of names. name arg
shoulbe be able to be repeated multiple times.
The args option to play "peace" where the lowest card wins.

'''
import random
import sys


class Card:
    COLORS = ['spades', 'clubs', 'hearts', 'diamonds']

    def __init__(self, color, value) -> None:
        self.card = (value, color)


class Deck:
    def __init__(self) -> None:
        self.cards = [Card(color, value).card for value in range(1, 14) for color in Card.COLORS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)


class Player:
    pile = []

    def __init__(self, name: str) -> None:
        self.name = name
        self.cards = []
        self.pile = []

    def draw_card(self) -> tuple:
        '''Take a card from the top of the deck.

        Returns:
            tuple: with card value and color, e.g. (4, 'spades')
        '''
        if not self.cards:
            sys.exit(f'No more cards left for {self.name}. Oponent won')

        return self.cards.pop(0)

    def add_cards(self, cards: list) -> None:
        '''Add card to the bottom of the deck.

        Args:
            cards (list): with card value and color, e.g. [(4, 'spades')]
        '''
        self.cards.append(cards)

        if Player.pile:
            print(f'Cards left in pile: {len(Player.pile)}')
            self.cards = Player.pile + self.cards
            Player.pile = []

    def cards_left(self):
        return len(self.cards)


def draw(p1: Player, p2: Player) -> None:
    c1, c2 = p1.draw_card(), p2.draw_card()
    print(f'{p1.name} "{c1[1]} {c1[0]}" vs {p2.name} "{c2[1]} {c2[0]}"')

    if c1[0] > c2[0]:
        p1.add_cards(c1)
        p1.add_cards(c2)
    elif c2[0] > c1[0]:
        p2.add_cards(c2)
        p2.add_cards(c1)
    else:
        print('Draw')
        Player.pile.extend([c1] + [c2] + [p1.draw_card()] + [p2.draw_card()])

    print(f'{p1.name} cards: {p1.cards_left()}, {p2.name} cards: {p2.cards_left()}')
    print('-' * 50)


def main() -> None:
    deck = Deck()

    player, computer = Player('Player'), Player('ClosedAI')
    player.cards, computer.cards = deck.cards[::2], deck.cards[1::2]

    round = 1
    while player.cards and computer.cards:
        print(f'Round {round}:')

        draw(player, computer)

        round += 1

        if not len(player.cards):
            print(f'{computer.name} won.')
        if not len(computer.cards):
            print(f'{player.name} won.')


if __name__ == '__main__':
    main()
