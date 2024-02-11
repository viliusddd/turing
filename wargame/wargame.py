import random


class Card:
    colors = ['spades', 'clubs', 'hearts', 'diamonds']

    def __init__(self, color, value) -> None:
        self.color = color
        self.value = value
        self.card = (value, color)

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
    pile = []

    def __init__(self, player, computer) -> None:
        self.player = player
        self.computer = computer

    def compare(self):
        if self.player_card > self.computer_card:
            pass


def main() -> None:
    deck = Deck()
    deck = deck.cards

    player = Player()
    computer = Computer()

    # deal 26 cards to each player
    player.cards, computer.cards = deck[::2], deck[1::2]

    # for i in enumerate(player.cards):
    #     print(player.cards[-1], computer.cards[-1])
    #     player.cards.pop(-1)
    #     computer.cards.pop(-1)

    war = War(player, computer)

    war_pile = []
    win = 0
    # flip cards
    for pl, cp in (zip(reversed(player.cards), reversed(computer.cards))):

        print(len(player.cards), pl, cp)
        if not war_pile:
            if pl[0] > cp[0]:
                player.pile.extend(pl+cp)
            elif pl[0] < cp[0]:
                computer.pile.extend(pl+cp)
            else:
                war.pile.extend(pl+cp)
        elif len(war_pile) % 2 == 0:
            war_pile.extend(pl+cp)
        elif len(war_pile) % 4 == 0:
            if pl[0] > cp[0]:
                player.pile.extend(cp+pl+war_pile)
                war.pile = []
            elif pl[0] < cp[0]:
                computer.pile.extend(cp+pl+war_pile)
                war.pile = []
            else:
                war_pile.extend(cp+pl)

        del computer.cards[-1]
        del player.cards[-1]

        # when deck finishes and both players have cards in pile: transfer pile cards to deck and
        # run loop again. Until one of the players won't have cards in both: deck and pile

    print(player.pile)
    print(computer.pile)


if __name__ == '__main__':
    main()