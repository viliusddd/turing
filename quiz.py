#! .venv/bin/python
'''
TODO: Interactive learning tool that allows users to create, practice,
and test their knowledge using multiple-choice and freeform text
questions. The program will track user statistics and provide
options to manage the questions.

Usage:
  ./quiz.py [options]
  ./quiz.py test|practice|question|stats|reset
  ./quiz.py stats [--id=<id>|--user=<username>] [--status=<status> --type=<type>]
  ./quiz.py profile [<username>|--user=<username>|--add-user=<username>|--remove-user=<username>]
  ./quiz.py question [--enabled|--remove|--update|--reset] <id>


Commands:
  test              Test mode
  practice          Practice mode
  question          Questions editing mode
  stats             Show statistics of questions
  profile           Create/change/see status of profile

Options:
  -h --help         Show this screen.
  -a --add          Add question
  -r --remove       Remove question
  --toggle-status   Toggle status of question from active to inactive
                    and vise versus.
  --all             Show all questions
  --active          Show active questions
  --inactive        Show inactive questions
#   --status          Choose to show only active or inactive questions
  --type            Choose to show free-form or multi-choice questions
  -v --verbose      Print verbose output to terminal: Print explanations
  -vv               Print very verbose output to terminal: print explanations and output tables
'''

import csv
import random

from docopt import docopt
from tabulate import tabulate


class Quiz:
    def __init__(self, filename):
        self.filename = filename
        self.db = []
        self._get_db()

    def _get_db(self):
        with open(self.filename) as file:
            self.db = list(csv.DictReader(file))
            for row in self.db:
                row['_id'] = int(row['_id'])
                row['times_shown'] = int(row['times_shown'])
                row['correct'] = int(row['correct'])

                if row['enabled'] == "True":
                    row['enabled'] = True
                else:
                    row['enabled'] = False

    def _save_db(self):
        with open(self.filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=[i for i in self.db[0]])
            writer.writeheader()
            writer.writerows(self.db)

    def freeform_question(self):
        for i, row in enumerate(self.db):
            print('-' * 80)
            print(f'{i + 1}. {row["question"]}')
            user_answer = input('Your answer: ')
            if user_answer == row['answer']:
                print('Success! Your answer is correct!')
                row['correct'] += 1
                row['times_shown'] += 1
            else:
                print(f'You are wrong. Correct answer: {row["answer"]}')
                row['times_shown'] += 1

        self._save_db()

    def quiz_question(self):
        """
        TODO: Error if write other Than A B C D
        """
        abc = ['A', 'B', 'C', 'D']

        for i, row in enumerate(self.db):
            print('-' * 80)
            print(f'{i + 1}. {row["question"]}')
            # print(row['choices'].split(', '))
            choices = row['choices'].split(', ')
            choices.append(row['answer'])
            random.shuffle(choices)
            choices = (dict(zip(abc, choices)))

            for letter, choice in choices.items():
                print(f'\t{letter}. {choice}')

            user_answer = input('Your answer: ')
            if choices[user_answer] == row['answer']:
                print('Success! Your answer is correct!')
                row['correct'] += 1
                row['times_shown'] += 1
            else:
                print(f'You are wrong. Correct answer: {row["answer"]}')
                row['times_shown'] += 1

        self._save_db()

    def add_question(self):
        # question;multiple_choices;correct_answer
        # if multipple_choices is omited, then it will be treated as
        # free-form question instead of quiz with multiple choices

        # free-form example: Capital of Poland;;Warsaw
        # quiz example: Capital of Poland;Vilnius, Riga, Kiev;Warsaw

        template = {
            '_id': max(row['_id'] for row in self.db) + 1,
            'status': 'active',
            'question': '',
            'choices': '',
            'answer': '',
            'times_shown': 0,
            'correct': 0,
        }

        question = input('Your question: ')
        question = question.split(';')

        template['question'] = question[0]
        template['choices'] = question[1]
        template['answer'] = question[2]

        self.db.append(template)
        self._save_db()

    def reset(self):
        for row in self.db:
            row['correct'] = 0
            row['times_shown'] = 0
        self._save_db()

    def _get_question_index(self, qid:int) -> int:
        index = 0
        for i, row in enumerate(self.db):
            if row['_id'] == int(qid):
                index = i
        return index

    def _tabulate_data(self, rows:list) -> str:
        table = tabulate(
            rows,
            headers='keys',
            tablefmt='rounded_grid',
            colalign=('right', 'center', 'left', 'left', 'left', 'center')
        )
        return table

    def question_status(self, qid:int) -> str:
        qu_index = self._get_question_index(int(qid))
        row = self.db[qu_index]
        return self._tabulate_data([row])

    def toggle_question_status(self, qid:int) -> str:
        qu_index = self._get_question_index(qid)
        row = self.db[qu_index]
        row['enabled'] = not row['enabled']

        self._save_db()
        return self._tabulate_data([row])

    def update_question(self, qid:int):
        qu_index = self._get_question_index(qid)
        row = self.db[qu_index]

        question = input('Your question: ')
        question = question.split(';')

        row['question'] = question[0]
        row['choices'] = question[1]
        row['answer'] = question[2]

        self._save_db()
        return self._tabulate_data([row])

    def reset_question(self, qid:int):
        qu_index = self._get_question_index(qid)
        row = self.db[qu_index]

        row['enabled'] = True
        row['times_shown'] = 0
        row['correct'] = 0

        self._save_db()
        return self._tabulate_data([row])

    def delete_question(self, qid:int):
        qu_index = self._get_question_index(qid)

        self.db.pop(qu_index)
        self._save_db()

    def status(self) -> str:
        """
        Show grid with questions and their status
        """
        for row in self.db:
            if row['choices']:
                row['type'] = 'multi-choice'
            else:
                row['type'] = 'free-form'

            row.pop('answer')
            row.pop('choices')

            if row['correct'] == 0:
                row['correct'] = '0%'
            else:
                row['correct'] = \
                    f'{row["times_shown"] / row["correct"] * 100}%'

        table = tabulate(
            self.db,
            headers='keys',
            tablefmt='rounded_grid',
            colalign=('right', 'center', 'left', 'left', 'left', 'center')
        )
        return table


def main():
    args = docopt(__doc__, version='0.01')

    q = Quiz('db1_short.csv')

    if args['stats']:
        print(q.status())

    if args['test']:
        q.quiz_question()

    # Questions manipulation
    if args['question']:
        if args['<id>']:
            if args['--enabled']:
                print(q.toggle_question_status(args['<id>']))
            elif args['--update']:
                q.update_question(args['<id>'])
            elif args['--reset']:
                q.reset_question(args['<id>'])
            elif args['--remove']:
                q.delete_question(args['<id>'])
            else:
                print(q.question_status(args['<id>']))

    # reset
    if args['reset']:
        q.reset()


if __name__ == '__main__':
    main()

# Link to the public GitHub repo tha contains my work from Part 3:
# TODO: https://github.com/viliusddd/turing/quiz


"""
TODO:
1. Add -v switch
2. Split to two classes: Questions and Quiz
3. Add confirmation dialog, e.g. do you really want to reset all questions? yN
"""