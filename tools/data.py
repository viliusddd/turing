import csv
import sys

from enum import Enum
from pprint import pprint

from dataclasses import dataclass, fields
from pprint import pprint


class QuestionType(Enum):
    QUIZ = 'quiz'
    FREE_FORM = 'freeform'


class QuestionStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


@dataclass
class Question:
    id: int
    definition: str
    answer: str
    choices: list
    status: QuestionStatus = QuestionStatus('active')
    type: QuestionType = QuestionType('quiz')
    correct: int = 0
    times_shown: int = 0

    def tight_dict(self):
        """
        Usual method of using <class_name>.__dict__ returns 'status'
        and 'type' values as classes names with values.
        """
        return {
            'id': self.id,
            'definition': self.definition,
            'answer': self.answer,
            'choices': ', '.join(self.choices),
            'status': self.status.value,
            'type': self.type.value,
            'correct': self.correct,
            'times_shown': self.times_shown
        }


class Data:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.db:list = []
        self.get()

    def get(self):
        with open(self.filename) as file:
            for row in csv.DictReader(file):
                choices = row['choices']
                if choices:
                    choices = choices.split(',')
                    choices = [ch.strip() for ch in choices]

                self.db.append(Question(
                    definition=row['definition'],
                    answer=row['answer'],
                    choices=choices,
                    id=int(row['id']),
                    type=QuestionType(row['type']),
                    status=QuestionStatus(row['status']),
                    correct=int(row['correct']),
                    times_shown=int(row['times_shown'])
                ))

    def get_dict(self):
        ...

    def save(self):

        with open(self.filename, 'w') as file:
            fieldnames = ['id', 'definition', 'answer', 'choices',
                          'status', 'type', 'correct', 'times_shown']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([i.tight_dict() for i in self.db])

    def save_row(self, new_row):
        for i, row in enumerate(self.db):
            if int(row.id) == int(new_row.id):
                self.db[i] = new_row
                self.save()
