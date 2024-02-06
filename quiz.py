#! .venv/bin/python
'''
TODO: Interactive learning tool that allows users to create, practice,
and test their knowledge using multiple-choice and freeform text
questions. The program will track user statistics and provide
options to manage the questions.

Usage:
  ./quiz.py [options]
  ./quiz.py test|practice|question|stats|reset
  ./quiz.py test [--amount=<amount>] [--mode=<mode>]
  ./quiz.py practice [--amount=<amount>] [--mode=<mode>]
  ./quiz.py stats [--id=<id>|--user=<username>] [--status=<status> --type=<type>]
  ./quiz.py profile [<username>|--user=<username>|--add-user=<username>|--remove-user=<username>]
  ./quiz.py question [--stats|--active|--remove|--update|--reset] <id>
  ./quiz.py question [--reset-all|--add|]

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
  --add             Add question
  --reset-all       Reset all questions numbers
'''
import csv
import random
import time

from docopt import docopt
from pprint import pprint
from tabulate import tabulate


class Profile:
    ...

class Data:
    def __init__(self, filename):
        self.filename = filename
        self.db = []
        self.get()

    def get(self):
        with open(self.filename) as file:
            self.db = list(csv.DictReader(file))
            for row in self.db:
                row['_id'] = int(row['_id'])
                row['times_shown'] = int(row['times_shown'])
                row['correct'] = int(row['correct'])

                if row['active'] == "True":
                    row['active'] = True
                else:
                    row['active'] = False

    def save(self):
        with open(self.filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=[i for i in self.db[0]])
            writer.writeheader()
            writer.writerows(self.db)

    def save_row(self, new_row):
        for i, row in enumerate(self.db):
            if int(row['_id']) == int(new_row['_id']):
                self.db[i] = new_row
                self.save()


class Question:
    def __init__(self, qid, filename):
        self.qid = qid or None
        self.data = Data(filename)
        self.db = self.data.db

    def _tabulate_data(self, rows:list) -> str:
        table = tabulate(
            rows,
            headers='keys',
            tablefmt='rounded_grid',
            colalign=('right', 'center', 'left', 'left', 'left', 'center')
        )
        return table

    def _get_question_index(self) -> int:
        index = 0
        for i, row in enumerate(self.db):
            if row['_id'] == int(self.qid):
                index = i
        return index

    def _filter_columns(self, active=True, choices=True):
        '''
        Choose which questions should be shown:
            with or without choices;
            active or inactive.
        '''
        enabled_db = []

        # for row in self.db:
        for row in self.db:
            if active and row['active']:
                enabled_db.append(row)
            elif active is False and row['active'] is False:
                enabled_db.append(row)

        choices_db = []
        for row in enabled_db:
            if choices and (row['choices'] != ''):
                choices_db.append(row)
            elif (not choices) and (row['choices'] == ''):
                choices_db.append(row)

        return(choices_db)

    def _rows_from_ids(self, qids:list) -> list:
        rows = []
        for row in self.db:
            for qid in qids:
                if row['_id'] == qid:
                    rows.append(row)

        return rows

    def _filter_by_mode(self, rows, mode='mixed'):
        '''
        There are 3 testing/practicing modes:
          - choosing: if mode is set to 'choosing' then user will only
                      get questions that have multiple choices;
          - typing: only questions that have answer but no multiple
                    choices;
          - mixed: user gets both types of questions and will need to
                   either type answer or choose a letter from multiple
                   choices.
        '''
        new_rows = []

        for row in rows:
            if row['active']:
                if mode == 'mixed':
                    new_rows = rows
                elif mode == 'typing':
                    if row['choices'] == '':
                        new_rows.append(row)
                elif mode == 'choosing':
                    if row['choices'] != '':
                        new_rows.append(row)
                else:
                    raise TypeError('Chosen the wrong answering mode')

        return new_rows

    def test(self, amount=5, answer_mode='mixed'):
        amount = int(amount)

        # if amount < 5:
        #     raise ValueError('At least 5 questions are required to start test.')

        rows = self._filter_by_mode(rows=self.db, mode=answer_mode)
        rows = random.sample(rows, amount)

        if amount > len(rows):
            raise ValueError(f'Required amount is lower than \
                             available questions. {amount}>{len(rows)}.')

        self._user_input(rows, amount)

    def _typing_input(self, row):
        while True:
            user_answer = input('Your answer: ')
            if user_answer:
                return user_answer

    def _choosing_input(self, row):
        abc = ['A', 'B', 'C', 'D', 'E', 'F']

        choices = row['choices'].split(', ')
        choices.append(row['answer'])

        random.shuffle(choices)
        choices = (dict(zip(abc, choices)))

        for letter, choice in choices.items():
            print(f'\t{letter}. {choice}')

        while True:
            user_letter = input('Choose letter: ')

            if user_letter.upper() in abc[:len(choices)]:
                return choices[user_letter]

    def _user_input(self, rows, amount):
        user_stats = {'correct': 0, 'total': 0, 'duration': ''}
        start_time = time.time()

        for i, row in enumerate(rows):
            print(f'{i + 1}. {row["question"]}')
            try:
                if row['choices'] != '':
                    user_answer = self._choosing_input(row)
                else:
                    user_answer = self._typing_input(row)
            except (EOFError, KeyboardInterrupt):
                print('\n' + '-' * 80)
                break
            else:
                if user_answer == row['answer']:
                    print('Success! Your answer is correct!')
                    row['correct'] += 1
                    user_stats['correct'] += 1
                else:
                    print(f'You are wrong. Correct answer: {row["answer"]}')

            print('-' * 80)
            row['times_shown'] += 1
            user_stats['total'] += 1

            self.data.save_row(row)

        user_stats['duration'] =  time.time() - start_time
        self._user_stats_msg(user_stats)

    def _user_stats_msg(self, stats:dict):
        total = f'{stats["correct"]}/{stats["total"]}'
        duration = time.strftime(
            "%M min %S sec.", time.gmtime(stats['duration'])
        )
        msg = f'{total} questions answered correctly.\n' \
              f'Test took {duration}'

        print(msg)
        # return

    def _filter_practice_questions(self):
        ...

    def _type(self):
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

        self.data.save()

    def add(self):
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
        self.data.save()

    def reset(self):
        qu_index = self._get_question_index()
        row = self.db[qu_index]

        row['active'] = True
        row['times_shown'] = 0
        row['correct'] = 0

        self.data.save()
        return self._tabulate_data([row])

    def reset_all(self):
        for row in self.db:
            row['correct'] = 0
            row['times_shown'] = 0
        self.data.save()

    def stats(self) -> str:
        qu_index = self._get_question_index()
        row = self.db[qu_index]
        return self._tabulate_data([row])

    def toggle_status(self) -> str:
        qu_index = self._get_question_index()
        row = self.db[qu_index]
        row['active'] = not row['active']

        self.data.save()
        return self._tabulate_data([row])

    def update(self):
        qu_index = self._get_question_index()
        row = self.db[qu_index]

        question = input('Your question: ')
        question = question.split(';')

        row['question'] = question[0]
        row['choices'] = question[1]
        row['answer'] = question[2]

        self.data.save()
        return self._tabulate_data([row])

    def remove(self):
        qu_index = self._get_question_index()

        self.db.pop(qu_index)
        self.data.save()

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
    # print(args)

    q = Question(args['<id>'], 'db1.csv')

    if args['stats']:
        print(q.status())

    # Practice

    # Test
    if args['test']:
        if args['--amount'] or args['--mode']:
            q.test(args['--amount'], args['--mode'])
        else:
            q.test()

    # Questions manipulation
    if args['question']:
        if args['<id>']:
            if args['--active']:
                print(q.toggle_status())
            elif args['--update']:
                print(q.update())
            elif args['--reset']:
                print(q.reset())
            elif args['--remove']:
                q.remove()
            elif args['--stats']:
                print(q.stats())
            else:
                print(q.stats())
        elif args['--add']:
            print(q.add())
        elif args['--reset-all']:
            q.reset_all()
        else:
            print(q.status())

    # reset
    if args['reset']:
        q.reset()


if __name__ == '__main__':
    main()

# Link to the public GitHub repo tha contains my work from Part 3:
# TODO: https://github.com/viliusddd/turing/


"""
TODO:
1. Add -v switch
3. Add confirmation dialog, e.g. do you really want to reset all questions? yN
4. Create class Question with __iter__ method https://dev.to/htv2012/how-to-write-a-class-object-to-csv-5be1
6. Implement question --disable=1; --disable=1,2,4,6; --disable=1-20
7. Fix that adding new  questions there wouldn't be spaces between answer,question,etc
8. Use python standard log library to output text to console?
"""