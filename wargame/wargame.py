import random


class Card:
    colors = ['spades', 'clubs', 'hearts', 'diamonds']

    def __init__(self, color, value) -> None:
        self.color = color
        self.value = value
        self.card = {color: value}

    def __str__(self):
        print(f'{self.value} of {self.suit}')

class Deck:
    def __init__(self) -> None:
        self.cards = [Card(color, value).card for value in range(1, 14) for color in Card.colors]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)


class Player:
    cards = []
    pile = []
    def __init__(self) -> None:
        pass

class Computer:
    cards = []
    pile = []
    def __init__(self) -> None:
        pass

    @classmethod
    def draw():
        card = Computer.cards[-1]
        del Computer.cards[card]
        return Computer.cards[-1]

class War:

    def __init__(self, player, computer):
        self.player = player
        self.computer = computer

    def compare(self):
        if self.player_card > self.computer_card:
            pass


def main():
    deck = Deck()
    deck = deck.cards

    player = Player()
    computer = Computer()

    player.cards, computer.cards = deck[::2], deck[1::2]

    for i in enumerate(player.cards):
        print(player.cards[-1], computer.cards[-1])
        player.cards.pop(-1)
        computer.cards.pop(-1)

    war = War(player, computer)


if __name__ == '__main__':
    main()