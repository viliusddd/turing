#! .venv/bin/python
'''
TODO: Interactive learning tool that allows users to create, practice,
and test their knowledge using multiple-choice and freeform text
questions. The program will track user statistics and provide
options to manage the questions.

Usage:
  quiz.py (test|practice|question|stats|reset) [--db=<db_file>] [--results=<file>]
  quiz.py test [--limit=<amount>] [--mode=<mode>]
  quiz.py practice [--mode=<mode>]
  quiz.py question <id> (stats|toggle|enable|disable|update|remove|reset)
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
  -m --mode=<mode>     One of modes: typing, choosing, mixed. [default: mixed].

  -v --verbose         Print verbose output to terminal: Print explanations
  --reset-all          Reset all questions numbers
  --results=<file>     Test results log file. [default: results.txt]
  --db=<db_file>       CSV for questions and stats keeping. [default: db.csv]

Arguments:
  <id>                 Id of question from the database/csv.

'''
import copy
import logging
import random
import time
import sys

from tabulate import tabulate

from tools.data import Data, Question, QuestionStatus, QuestionType
from tools.questions import ModifyQuestion
from tools.docopt import docopt


class Quiz:
    def __init__(self, qids, data):
        self.data = data
        self.qids = qids or None
        self.ids = self._split_question_ids() if qids else None

    def print_stats(self, rows: list = None, all=None) -> str:
        if all:
            rows = self.data.db

        if not rows:
            rows = [row for row in self.data.db if row.id in self.ids]

        rows = copy.deepcopy(rows)

        for row in rows:
            row.choices = ', '.join(row.choices)
            row.status = row.status.value
            row.type = row.type.value

        if rows:
            print(tabulate(rows, headers='keys', tablefmt='rounded_grid'))
        else:
            print('The row doesn\'t exist')

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
            for i, row in enumerate(self.data.db):
                if qid == row.id:
                    indexes.append(i)
        return indexes

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

        for row in self.data.db:
            if row.status.value == 'active':
                if mode == 'mixed':
                    new_rows = self.data.db
                elif mode == 'typing':
                    if row.choices == '':
                        new_rows.append(row)
                elif mode == 'choosing':
                    if row.choices != '':
                        new_rows.append(row)
                else:
                    raise TypeError('Chosen the wrong answering mode')

        return new_rows

    def weighted_choices(self, rows):
        weights = []
        for row in rows:
            if row.correct == 0:
                weights.append(9.9)
            else:
                ratio = 10 - (row.correct / row.times_shown * 10)
                weight = round(ratio, 1)
                if weight == 0:
                    weight = 0.5
                weights.append(weight)

        rows = random.choices(rows, weights=weights, k=(int(len(rows))))
        return rows

    def practice(self, answer_mode='mixed'):
        rows = self._filter_by_mode(mode=answer_mode)
        rows = random.sample(rows, len(rows))

        self._user_input(rows, limited=False)

    def test(self, amount=5, answer_mode='mixed'):
        amount = int(amount)

        # if amount < 5:
        #     raise ValueError('At least 5 questions required to start test.')

        rows = self._filter_by_mode(mode=answer_mode)
        rows = random.sample(rows, amount)

        if amount > len(rows):
            raise ValueError(f'Required amount is lower than \
                             available questions. {amount}>{len(rows)}.')

        self._user_input(rows, limited=True)

    def _typing_input(self):
        while True:
            user_answer = input('Your answer: ')
            if user_answer:
                return user_answer

    def _choosing_input(self, row):
        abc = ['A', 'B', 'C', 'D', 'E', 'F']

        choices = row.choices
        choices.append(row.answer)

        random.shuffle(choices)
        choices = (dict(zip(abc, choices)))

        for letter, choice in choices.items():
            print(f'\t{letter}. {choice}')
            if choice == row.answer:
                i = row.choices.index(choice)
                del row.choices[i]

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
                    print(f'{num}. {row.definition}')

                    if row.choices:
                        user_answer = self._choosing_input(row)
                    else:
                        user_answer = self._typing_input()

                    if user_answer == row.answer:
                        print('Success! Your answer is correct!')
                        row.correct += 1
                        user_stats['correct'] += 1
                    else:
                        print(f'You\'re wrong. Right answer: {row.answer}')

                    print('-' * 80)
                    row.times_shown += 1
                    user_stats['total'] += 1

                    self.data.save_row(row)

                    num += 1

                if limited:
                    break

        except (EOFError, KeyboardInterrupt):
            print('\n' + '-' * 80)

        user_stats['duration'] = time.time() - start_time

        self._user_stats_msg(user_stats)

    def _user_stats_msg(self, stats: dict):
        total = f'{stats["correct"]}/{stats["total"]}'
        total_perc = f'{stats["correct"] / stats["total"] * 100:.0f}%'

        duration = time.strftime("%M min %S sec.",
                                 time.gmtime(stats['duration']))

        logging.info(
            f'{total_perc} ({total}) correct answers. Test took {duration}'
        )

    def add(self):
        # question;multiple_choices;correct_answer
        # if multipple_choices is omited, then it will be treated as
        # free-form question instead of quiz with multiple choices

        # free-form example: Capital of Poland;;Warsaw
        # quiz example: Capital of Poland;Vilnius, Riga, Kiev;Warsaw

        try:
            last_id = max(row.id for row in self.data.db)
        except ValueError:
            last_id = 0

        preview_row = [row for row in self.data.db if row.id == last_id]

        print('Example question:\n')
        self.print_stats(preview_row)

        qu = input('Your question;answer;choices;type: ').strip().split(';')

        choices = [ch.strip() for ch in qu[2].split(',')]
        choices = list(filter(None, choices))  # remove empties

        if len(choices) == 0 and qu[3] == 'quiz':
            raise ValueError('There are no choices, but type is selected as quiz.')

        row = Question(
            id=last_id + 1,
            definition=qu[0],
            answer=qu[1],
            choices=choices,
            type=QuestionType(qu[3]),
        )
        self.data.db.append(row)
        self.data.save()

        self.print_stats([row])

    def reset(self):
        for row in self.data.db:
            for id in self.ids:
                if row.id == id:
                    row.status = QuestionStatus('active')
                    row.times_shown = 0
                    row.correct = 0
        self.data.save()
        self.print_stats()

    def reset_all(self):
        for row in self.data.db:
            row.correct = 0
            row.times_shown = 0
        self.data.save()

    def toggle_status(self) -> str:
        for row in self.data.db:
            for id in self.ids:
                if row.id == id:
                    if row.status.value == 'inactive':
                        row.status = QuestionStatus('active')
                    elif row.status.value == 'active':
                        row.status = QuestionStatus('inactive')

        self.data.save()
        self.print_stats()

    def enable(self) -> str:
        for row in self.data.db:
            for id in self.ids:
                if row.id == id:
                    if row.status.value == 'inactive':
                        row.status = QuestionStatus('active')
        self.data.save()
        self.print_stats()

    def disable(self) -> str:
        for row in self.data.db:
            for id in self.ids:
                if row.id == id:
                    if row.status.value == 'active':
                        row.status = QuestionStatus('inactive')
        self.data.save()
        self.print_stats()

    def update(self):
        # <question>;<multiple answer options>;<true answer>
        # input example: Whats your question?;One, Two answer;Correct answer

        for id in self.ids:
            for row in self.data.db:
                if row.id == id:
                    self.print_stats([row])

                    qu = input('Your question;answer;choices;type: ').strip().split(';')

                    choices = [ch.strip() for ch in qu[2].split(',')]
                    choices = list(filter(None, choices))  # remove empties

                    row.definition = qu[0]
                    row.answer = qu[1]
                    row.choices = choices
                    row.type = QuestionType(qu[3])

                    print(len(row.choices), row.choices)
                    if len(row.choices) == 0 and row.type.value == 'quiz':
                        msg = 'Type is selected as quiz, but no choices added.'
                        raise ValueError(msg)

        self.data.save()
        self.print_stats()

    def remove(self):
        indexes = self._get_questions_index()
        indexes.sort()

        for i, _ in reversed(list(enumerate(self.data.db))):
            if i in indexes:
                self.data.db.pop(i)

        self.data.save()

    def reset_db(self):
        self.data.db = []
        self.data.save()


def init_logging(filename):
    '''
    Logs messages to file and stdout. Both use different formatting.
    '''
    cli_formatter = logging.Formatter('%(message)s')
    std_formatter = logging.Formatter('%(asctime)s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(std_formatter)
    rootLogger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(cli_formatter)
    rootLogger.addHandler(console_handler)


def main():
    args = docopt(__doc__, version='0.01')

    results_name = 'results.txt'
    if args['--results']:
        results_name = args['--results']

    db_name = 'db1.csv'
    if args['--db']:
        db_name = args['--db']

    init_logging(results_name)

    data = Data(filename=db_name)
    q = Quiz(args['<id>'], data)

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
                q.toggle_status()
            elif args['disable']:
                q.disable()
            elif args['enable']:
                q.enable()
            elif args['update']:
                q.update()
            elif args['reset']:
                q.reset()
            elif args['remove']:
                q.remove()
            elif args['stats']:
                q.print_stats()
        elif args['add']:
            q.add()
        elif args['reset-all']:
            q.reset_all()
        else:
            q.status()
    elif args['reset']:
        q.reset_db()
    elif args['stats']:
        q.print_stats(all=True)


if __name__ == '__main__':
    main()

# Link to the public GitHub repo tha contains my work from Part 3:
# TODO: https://github.com/viliusddd/turing/

"""
TODO:
3. Add confirmation dialog, e.g. do you really want to reset all questions? yN
- The user should not be able to enter practice or test modes until at least 5
  questions have been added.
- double-check if disabled questions are shown in practice and test
- unit tests: at least 3
"""
