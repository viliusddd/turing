#! .venv/bin/python
'''
TODO: Interactive learning tool that allows users to create, practice,
and test their knowledge using multiple-choice and freeform text
questions. The program will track user statistics and provide
options to manage the questions.

Usage:
  quiz.py test | practice | question | stats | reset
  quiz.py test [--limit=<amount>] [--mode=<mode>]
  quiz.py practice [--mode=<mode>]
  quiz.py question (stats|toggle|enable|disable|update|remove|reset) <id>
  quiz.py question (reset-all|add)

Try:
  quiz.py test --limit 10 --mode typing
  quiz.py practice
  quiz.py stats
  quiz.py question add
  quiz.py question disable 2-7
  quiz.py question toggle 1,6,7

Commands:
  test                 Test mode
  practice             Practice mode
  question             Questions editing mode
  stats                Show statistics of questions
  reset                Remove all question

Options:
  -h --help            Show this screen.
  -a --add             Add question
  -r --remove          Remove question.
  --toggle-status      Toggle status of question from active to inactive
                       and vice versus.
  -l --limit=<amount>  Number of test questions to run. [default: 5].
  -m --mode=<mode>     One of the modes: typing, choosing, mixed. [default: mixed].

  -v --verbose         Print verbose output to terminal: Print explanations
  -vv                  Print very verbose output to terminal: print explanations and output tables
  --reset-all          Reset all questions numbers

Arguments:
  <id>                 Id of question from the database/csv.

'''
import csv
import random
import time

from docopt import docopt
from pprint import pprint
from tabulate import tabulate


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
    def __init__(self, qids, filename):
        self.qids = qids or None
        self.data = Data(filename)
        self.db = self.data.db

    def _tabulate_data(self, rows:list) -> str:
        table = tabulate(
            rows,
            headers='keys',
            tablefmt='rounded_grid',
            colalign=('right', 'center', 'right')
        )
        return table

    def _split_question_ids(self) -> list:
        if self.qids.isdigit():
            qids = [int(self.qids)]
        elif ',' in self.qids:
            qids = self.qids.split(',')
            qids = [int(qid) for qid in qids]
        elif '-' in self.qids:
            qid1, qid2 = self.qids.split('-')
            qids = list(range(int(qid1), int(qid2) + 1))
        else:
            raise ValueError('Wrong question id or or ids range.')
        return qids

    def _get_questions_index(self) -> list:
        qids = self._split_question_ids()

        indexes = []
        for qid in qids:
            for i, row in enumerate(self.db):
                if qid == row['_id']:
                    indexes.append(i)
        return indexes

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

    def _filter_by_mode(self, mode='mixed'):
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

        for row in self.db:
            if row['active']:
                if mode == 'mixed':
                    new_rows = self.db
                elif mode == 'typing':
                    if row['choices'] == '':
                        new_rows.append(row)
                elif mode == 'choosing':
                    if row['choices'] != '':
                        new_rows.append(row)
                else:
                    raise TypeError('Chosen the wrong answering mode')

        return new_rows

    def weighted_choices(self, rows):
        weights = []
        for row in rows:
            if row['correct'] == 0:
                weights.append(9.9)
            else:
                weight = round(10 - (row['correct'] / row['times_shown'] * 10), 1)
                if weight == 0:
                    weight = 0.5
                weights.append(weight)

        rows = random.choices(rows, weights=weights, k=(int(len(rows))))
        return(rows)

    def practice(self, answer_mode='mixed'):
        rows = self._filter_by_mode(mode=answer_mode)
        rows = random.sample(rows, len(rows))

        self._user_input(rows, limited=False)

    def test(self, amount=5, answer_mode='mixed'):
        amount = int(amount)

        # if amount < 5:
        #     raise ValueError('At least 5 questions are required to start test.')

        rows = self._filter_by_mode(mode=answer_mode)
        rows = random.sample(rows, amount)

        if amount > len(rows):
            raise ValueError(f'Required amount is lower than \
                             available questions. {amount}>{len(rows)}.')

        self._user_input(rows, limited=True)

    def _typing_input(self, row):
        while True:
            user_answer = input('Your answer: ')
            if user_answer:
                return user_answer

    def _choosing_input(self, row):
        abc = ['A', 'B', 'C', 'D', 'E', 'F']

        choices = row['choices'].split(',')
        choices = [ch.strip() for ch in choices]
        choices.append(row['answer'])

        random.shuffle(choices)
        choices = (dict(zip(abc, choices)))

        for letter, choice in choices.items():
            print(f'\t{letter}. {choice}')

        while True:
            user_letter = input('Choose letter: ')

            if user_letter.upper() in abc[:len(choices)]:
                return choices[user_letter.upper()]

    def _user_input(self, rows, limited=False):
        user_stats = {'correct': 0, 'total': 0, 'duration': ''}
        start_time = time.time()

        try:
            num = 1
            while True:
                if not limited:
                    self.weighted_choices(rows)
                for row in rows:
                    print(f'{num}. {row["question"]}')

                    if row['choices'] != '':
                        user_answer = self._choosing_input(row)
                    else:
                        user_answer = self._typing_input(row)

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

                    num += 1

                if limited:
                    break

        except (EOFError, KeyboardInterrupt):
            print('\n' + '-' * 80)

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

    def add(self, question=None):
        # question;multiple_choices;correct_answer
        # if multipple_choices is omited, then it will be treated as
        # free-form question instead of quiz with multiple choices

        # free-form example: Capital of Poland;;Warsaw
        # quiz example: Capital of Poland;Vilnius, Riga, Kiev;Warsaw

        row = {
            '_id': max(row['_id'] for row in self.db) + 1,
            'active': True,
            'question': '',
            'choices': '',
            'answer': '',
            'times_shown': 0,
            'correct': 0,
        }

        if not question:
            question = input('Your question: ')

        question = question.split(';')

        row['question'] = question[0]
        row['choices'] = question[1]
        row['answer'] = question[2]

        self.db.append(row)
        self.data.save()

        return self._tabulate_data([row])

    def reset(self):
        qs_index = self._get_questions_index()
        rows = []
        for index in qs_index:
            rows.append(self.db[index])
            self.db[index]['active'] = True
            self.db[index]['times_shown'] = 0
            self.db[index]['correct'] = 0

        self.data.save()
        return self._tabulate_data(rows)

    def reset_all(self):
        for row in self.db:
            row['correct'] = 0
            row['times_shown'] = 0
        self.data.save()

    def stats(self) -> str:
        qs_index = self._get_questions_index()
        rows = []
        for index in qs_index:
            rows.append(self.db[index])

        return self._tabulate_data(rows)

    def toggle_status(self) -> str:
        qs_index = self._get_questions_index()
        rows = []
        for index in qs_index:
            rows.append(self.db[index])
            self.db[index]['active'] ^= True

        self.data.save()
        return self._tabulate_data(rows)

    def enable(self) -> str:
        qs_index = self._get_questions_index()
        rows = []
        for index in qs_index:
            self.db[index]['active'] = True
            rows.append(self.db[index])

        self.data.save()
        return self._tabulate_data(rows)

    def disable(self) -> str:
        qs_index = self._get_questions_index()
        rows = []
        for index in qs_index:
            self.db[index]['active'] = False
            rows.append(self.db[index])

        self.data.save()
        return self._tabulate_data(rows)

    def update(self):
        # <question>;<multiple answer options>;<true answer>
        # input example: Whats your question?;One, Two answer;Correct answer
        qs_index = self._get_questions_index()

        rows = []

        for index in qs_index:
            row = self.db[index]

            print(self._tabulate_data([row]))

            question = input('Your question: ')
            question = question.split(';')

            row['question'] = question[0]
            row['choices'] = question[1]
            row['answer'] = question[2]

            rows.append(row)

        self.data.save()
        return self._tabulate_data(rows)

    def remove(self):
        indexes = self._get_questions_index()
        indexes.sort()

        for i, _ in reversed(list(enumerate(self.db))):
            if i in indexes:
                self.db.pop(i)

        self.data.save()

    def status(self) -> str:
        """
        Show grid with questions and their status
        """
        for row in self.db:
            if row['correct'] == 0:
                row['correct'] = '0%'
            else:
                row['correct'] = \
                    f'{row["correct"] / row["times_shown"] * 100:.0f}%'

        table = tabulate(
            self.db,
            headers='keys',
            tablefmt='rounded_grid',
            colalign=('right', 'center', 'right')
        )
        return table


def main():
    args = docopt(__doc__, version='0.01')
    # print(args)

    q = Question(args['<id>'], 'db1.csv')

    # Practice
    if args['practice']:
        if args['--mode']:
            q.practice(args['--mode'])
        else:
            q.practice()
    # Test
    elif args['test']:
        if args['--limit'] or args['--mode']:
            q.test(args['--limit'], args['--mode'])
        else:
            q.test()
    # Questions manipulation
    elif args['question']:
        if args['<id>']:
            if args['toggle']:
                print(q.toggle_status())
            elif args['disable']:
                print(q.disable())
            elif args['enable']:
                print(q.enable())
            elif args['update']:
                print(q.update())
            elif args['reset']:
                print(q.reset())
            elif args['remove']:
                q.remove()
            elif args['stats']:
                print(q.stats())
        elif args['add']:
            # print(q.add(args['--add']))
            print(q.add())
        elif args['reset-all']:
            q.reset_all()
        else:
            print(q.status())
    elif args['reset']:
        q.reset()
    elif args['stats']:
        print(q.status())

if __name__ == '__main__':
    main()

# Link to the public GitHub repo tha contains my work from Part 3:
# TODO: https://github.com/viliusddd/turing/


"""
TODO:
1. Add -v switch
3. Add confirmation dialog, e.g. do you really want to reset all questions? yN
4. Create class Question with __iter__ method https://dev.to/htv2012/how-to-write-a-class-object-to-csv-5be1
8. Use python standard log library to output text to console?
9. Fix question ids 5,9 breaking grid print. Question, choices, answer
   columns should increase in height for those lines.
- switch to change db file
- show help on app start without args
- fix ./quiz.py question stats 1 : two tables
- The user should not be able to enter practice or test modes until at least 5 questions have been added.
- double-check if disabled questions are shown in practice and test
- test should save results.txt file with the list of scores. add date and time.
- unit tests: at least 3
- run flake8
- add option to remove all questions?
"""