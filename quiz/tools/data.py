import csv

from enum import Enum
from dataclasses import dataclass


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

    def tight_dict(self) -> dict:
        """
        Returns "cleaned-up" version of dictionary, that
        Question.__dict__ usually returns. Without classes names
        in it or unnecessary double qotes or brackets.
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
    '''
    Read and write operations to main questions database CSV file.
    '''
    def __init__(self, filename) -> None:
        self.filename = filename
        self.db: list = []
        self.get()

    def get(self) -> None:
        '''
        Read CSV file and create dataclass object from it.
        '''
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

    def save(self) -> None:
        '''
        Write whole database to file.
        '''
        with open(self.filename, 'w') as file:
            fieldnames = ['id', 'definition', 'answer', 'choices',
                          'status', 'type', 'correct', 'times_shown']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([i.tight_dict() for i in self.db])

    def save_row(self, new_row) -> None:
        '''
        Replace existing row with "new" row and save.
        '''
        for i, row in enumerate(self.db):
            if int(row.id) == int(new_row.id):
                self.db[i] = new_row
                self.save()
