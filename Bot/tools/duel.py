import random

from Bot.tools.emoji import EmojiList
from Bot.database.models import Users


class Duel:
    duel_data = dict()

    def __init__(self, user_1:Users, user_2:Users):
        self.step = 0
        self.turn = user_1
        self.user_1 = user_1
        self.user_2 = user_2
        self.user_1_points = 0
        self.user_2_points = 0
        self.emoji = random.choice(EmojiList.emoji)

    def update_points(self, user:Users, points:int) -> None:
        if user == self.user_1:
            self.user_1_points += points
            self.turn = self.user_2
        else:
            self.user_2_points += points
            self.turn = self.user_1

        self.step += 1

    def get_winner(self) -> Users or None:
        if self.user_1_points > self.user_2_points:
            return self.user_1
        elif self.user_2_points > self.user_1_points:
            return self.user_2
        else:
            None