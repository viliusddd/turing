#! .venv/bin/python
'''
Interactive learning tool that allows users to create, practice,
and test their knowledge using multiple-choice and freeform text
questions. The program will track user statistics and provide
options to manage the questions.

Usage:
  quiz.py (test|practice|question|stats) [--db=<db_file>]
  quiz.py test [--limit=<amount>] [--mode=<mode>] [--results=<file>]
  quiz.py practice [--mode=<mode>] [--db=<db_file>]
  quiz.py question (stats|toggle|enable|disable|update|remove|reset) <id> [--db=<db_file>]
  quiz.py question (add|reset-all|remove-all) [--db=<db_file>]

Try:
  quiz.py test --limit 10 --mode freeform
  quiz.py practice
  quiz.py stats
  quiz.py question add
  quiz.py question disable 2-7
  quiz.py question toggle 1,6,7

Commands:
  test                  Test against limited number of questions. Results
                        are saved to the file.
  practice              Practice against unlimited number of questions
                        until you cancel it with Ctrl-D or Ctrl-C.
  question              Edit existing questions by supplying id(s), or add
                        a new one.
  stats                 Show statistics of all questions.

Options:
  -h --help             Show this screen.
  --results=<file>      Change testresults filepath. [default: results.txt]
  --db=<db_file>        Change db filepath.

Test and Practice:
  -l --limit=<amount>   Number of test questions to run. Default is 5
  -m --mode=<mode>      One of modes: freeform, quiz or mixed. Default is mixed.

Question:
  stats                 Show question(s) statistics.
  toggle                Toggle question(s) status from active to inactive or
                        vice versa.
  enable                Change question(s) status to active.
  disable               Change question(s) status to inactive.
  add                   Add new question. Command prompt is used for use input.
                        The template for user input: <question>;<answer>;<choices>;<type>.
                        <choices> is left empty if question type is freeform.
                        <type> can be only 'freeform' or 'quiz'
                        Examples: Lithuania capital?;Vilnius;;freeform
                                  Latvia capital?;Riga;Warsaw,Vilnius, Talin;quiz
  update                Update existing question(s). Refer to `add` for example.
  remove                Remove question(s) from db.
  remove-all            Remove all questions from db.
  reset                 Reset question(s) statistics.
  reset-all             Reset all questions statistics.

Arguments:
  <id>                  Existing dd of question from the database/csv.
'''
import copy
import logging
import random
import sys
import time

from tabulate import tabulate

from tools.data import Data, Question, QuestionStatus, QuestionType
from tools.docopt import docopt
from tools.utilities import query_yes_no, logger


class Quiz:
    '''
    A class to do quizing and question(s) manipulation.

    Attributes:
        qids (str): single or multipe question ids.
        data (Data): object responsible for read/write operations to db.
    '''
    def __init__(self, qids, data) -> None:
        self.data = data
        self.qids = qids or None
        self.ids = self._split_question_ids() if qids else None

    def _split_question_ids(self) -> list:
        '''Convert str of ids to list.

        Raises:
            ValueError: if value is not number(s) and/or can't be split
                        or id(s) not on db.

        Returns:
            list: of question ids, e.g.: [3] or [1,3,5,6]
        '''
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

        all_ids = [row.id for row in self.data.db]
        missing_ids = [str(id) for id in qids if id not in all_ids]

        if missing_ids:
            raise ValueError(
                f'Some ids aren\'t found in db: {", ".join(missing_ids)}'
            )
        return qids

    def _get_questions_index(self) -> list:
        '''
        Changes ids to indexes of questions in db.

        Returns:
            list: of indexes, e.g. [2] or [3, 4, 5]
        '''
        indexes = []
        for qid in self.ids:
            for i, row in enumerate(self.data.db):
                if qid == row.id:
                    indexes.append(i)
        return indexes

    def _filter_by_mode(self, mode: str = 'mixed') -> list:
        '''
        There are 3 modes in testing and practicing: quiz, freeform and
        mixed. Depending on the user choice either of those will be
        returned.

        Args:
            mode (str, optional): quiz, freeform or mixed.
                                  Defaults to 'mixed'.

        Raises:
            TypeError: if neiter of three modes where typed.

        Returns:
            list: of Question objects.
        '''
        new_rows = []

        for row in self.data.db:
            if row.status.value == 'active':
                if mode == 'mixed':
                    new_rows.append(row)
                elif mode == 'freeform':
                    if row.type.value == 'freeform':
                        new_rows.append(row)
                elif mode == 'quiz':
                    if row.type.value == 'quiz':
                        new_rows.append(row)
                else:
                    raise TypeError('Chosen the wrong answering mode')

        return new_rows

    def _freeform_input(self) -> str:
        '''
        User input to freeform question.

        Returns:
            str: user answer to freeform question.
        '''
        while True:
            user_answer = input('Your answer: ')
            if user_answer:
                return user_answer

    def _quiz_input(self, row: Question) -> str:
        '''
        Gets and validates user input against available choices for
        that particular question.

        Args:
            row (Question): object containing question attributes.

        Returns:
            str: user answer to question, e.g. 'Dublin'
        '''
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

    def _run_testing(self, rows: list, limited: bool = False) -> None:
        '''
        Gives user questions indefinitely or until limit is reached.

        Args:
            rows (list): of Question objects
            limited (bool, optional): if test/practice have limit of
                                      questions. Defaults to False.
        '''
        user_stats = {'correct': 0, 'total': 0, 'duration': ''}
        start_time = time.time()

        try:
            num = 1
            while True:
                if not limited:
                    self._weighted_choices(rows)
                for row in rows:
                    print(f'{num}. {row.definition}')

                    if row.choices:
                        user_answer = self._quiz_input(row)
                    else:
                        user_answer = self._freeform_input()

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

    def _user_stats_msg(self, stats: dict) -> None:
        '''
        Print user test statistics to terminal. Test statistics are also
        outputed to file with.

        Args:
            stats (dict): of statistics, e.g.:
                          {
                            'correct': 1,
                            'total': 6,
                            'duration': 14.929275274276733
                          }
        '''
        total = f'{stats["correct"]}/{stats["total"]}'
        total_perc = f'{stats["correct"] / stats["total"] * 100:.0f}%'

        duration = time.strftime("%M min %S sec.",
                                 time.gmtime(stats['duration']))

        logging.info(
            f'{total_perc} ({total}) correct answers. Test took {duration}'
        )

    def _weighted_choices(self, rows: list) -> list:
        '''
        Selects random questions from list by the probability of it.
        Questions with lower success rate will show-up more often.

        Args:
            rows (list): of Question objects.

        Returns:
            list: of Question objects that has weighted random choice applied.
        '''
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

    def test(self, amount: int = 5, answer_mode: str = 'mixed') -> None:
        '''
        Test user for a limited amount of questions.

        Args:
            amount (int, optional): amount of questions to test against.
                                    Defaults to 5.
            answer_mode (str, optional): either quiz, freeform or mixed.
                                         Defaults to 'mixed'.
        Raises:
            ValueError: the number of questions in db that matches
                        parameters is lower than requested.
        '''
        amount = int(amount)

        rows = self._filter_by_mode(mode=answer_mode)

        if len(rows) < 5:
            sys.exit('At least 5 available questions required to start test.')

        if amount > len(rows):
            raise ValueError('Required amount of questions is lower than '
                             f'available questions. {amount}>{len(rows)}.')

        rows = random.sample(rows, amount)

        self._run_testing(rows, limited=True)

    def practice(self, answer_mode: str = 'mixed') -> None:
        '''Practice on questions that might repeat until exit.

        Args:
            answer_mode (str, optional): either quiz, freeform or mixed.
                                         Defaults to 'mixed'.
        '''
        rows = self._filter_by_mode(mode=answer_mode)
        rows = random.sample(rows, len(rows))

        self._run_testing(rows, limited=False)

    def add(self) -> None:
        '''Append new question to the end of db.

        Command prompt is used for use input.
        The template for user input: <question>;<answer>;<choices>;<type>.
        <choices> is left empty if question type is freeform.
        <type> can be only 'freeform' or 'quiz'
        Examples:
            Capital of Lithuania?;Vilnius;;freeform
            Capital of Latvia?;Riga;Warsaw,Vilnius, Talin;quiz

        Raises:
            ValueError: if <quiz> is typed, but there are no <choices> present.
        '''
        try:
            last_id = max(row.id for row in self.data.db)
        except ValueError:
            last_id = 0

        preview_row = [row for row in self.data.db if row.id == last_id]

        print('Example question:\n')
        self.print_stats(preview_row)

        qu = input('question;answer;choices;type: ').strip().split(';')

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

    def remove(self) -> None:
        '''
        Remove question(s).
        '''
        indexes = self._get_questions_index()
        indexes.sort()

        for i, _ in reversed(list(enumerate(self.data.db))):
            if i in indexes:
                self.data.db.pop(i)

        self.data.save()

    def reset(self) -> None:
        '''
        Reset question(s) statistics.
        '''
        for row in self.data.db:
            for id in self.ids:
                if row.id == id:
                    row.status = QuestionStatus('active')
                    row.times_shown = 0
                    row.correct = 0
        self.data.save()
        self.print_stats()

    def reset_all(self) -> None:
        '''
        Reset all questions statistics.
        '''
        for row in self.data.db:
            row.correct = 0
            row.times_shown = 0
        self.data.save()

    def toggle_status(self) -> None:
        '''
        Toggle question(s) status from active to inactive and vice versa.
        '''
        for row in self.data.db:
            for id in self.ids:
                if row.id == id:
                    if row.status.value == 'inactive':
                        row.status = QuestionStatus('active')
                    elif row.status.value == 'active':
                        row.status = QuestionStatus('inactive')

        self.data.save()
        self.print_stats()

    def enable(self) -> None:
        '''
        Change question(s) status from inactive to active.
        '''
        for row in self.data.db:
            for id in self.ids:
                if row.id == id:
                    if row.status.value == 'inactive':
                        row.status = QuestionStatus('active')
        self.data.save()
        self.print_stats()

    def disable(self) -> None:
        '''
        Change question(s) status from active to inactive.
        '''
        for row in self.data.db:
            for id in self.ids:
                if row.id == id:
                    if row.status.value == 'active':
                        row.status = QuestionStatus('inactive')
        self.data.save()
        self.print_stats()

    def update(self) -> None:
        '''Update existing question(s) definition, answer, choices or type.

        Command prompt is used for use input.
        The template for user input: <question>;<answer>;<choices>;<type>.
        <choices> is left empty if question type is freeform.
        <type> can be only 'freeform' or 'quiz'
        Examples:
            Capital of Lithuania?;Vilnius;;freeform
            Capital of Latvia?;Riga;Warsaw,Vilnius, Talin;quiz

        Raises:
            ValueError: if <quiz> is typed, but there are no <choices> present.
        '''
        for id in self.ids:
            for row in self.data.db:
                if row.id == id:
                    self.print_stats([row])

                    qu = input('question;answer;choices;type: ').strip().split(';')

                    choices = [ch.strip() for ch in qu[2].split(',')]
                    choices = list(filter(None, choices))  # remove empties

                    row.definition = qu[0]
                    row.answer = qu[1]
                    row.choices = choices
                    row.type = QuestionType(qu[3])

                    if len(row.choices) == 0 and row.type.value == 'quiz':
                        msg = 'Type is selected as quiz, but no choices added.'
                        raise ValueError(msg)
        self.data.save()
        self.print_stats()

    def reset_db(self) -> None:
        '''
        Delete all existing questions.
        '''
        if query_yes_no('Do you really want to delete all the questions?'):
            self.data.db = []
            self.data.save()

    def print_stats(self, rows: list = None, all=None) -> None:
        '''
        Output to terminal one or more questions attributes in a
        tabulated form.

        Args:
            rows (list, optional): list of Question objects. Defaults to None.
            all (_type_, optional): if True then all questions are printed.
                                    Defaults to None.
        '''
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
            print('No questions are present in database.')


def main() -> None:
    '''
    Defines interface for cli arguments.
    '''
    args = docopt(__doc__, version='0.01')

    results_name = 'results.txt'
    if args['--results']:
        results_name = args['--results']
    logger(results_name)

    db_name = 'db.csv'
    if args['--db']:
        db_name = args['--db']

    data = Data(filename=db_name)
    quiz = Quiz(args['<id>'], data)

    # Practice
    if args['practice']:
        if args['--mode']:
            quiz.practice(args['--mode'])
        else:
            quiz.practice()

    # Test
    elif args['test']:
        if args['--limit'] and args['--mode']:
            quiz.test(amount=args['--limit'], answer_mode=args['--mode'])
        elif args['--limit']:
            quiz.test(amount=args['--limit'])
        elif args['--mode']:
            quiz.test(answer_mode=args['--mode'])
        else:
            quiz.test()

    # Questions manipulation
    elif args['question']:
        if args['<id>']:
            if args['toggle']:
                quiz.toggle_status()
            elif args['disable']:
                quiz.disable()
            elif args['enable']:
                quiz.enable()
            elif args['update']:
                quiz.update()
            elif args['reset']:
                quiz.reset()
            elif args['remove']:
                quiz.remove()
            elif args['stats']:
                quiz.print_stats()
        elif args['add']:
            quiz.add()
        elif args['reset-all']:
            quiz.reset_all()
        elif args['remove-all']:
            quiz.reset_db()
    elif args['stats']:
        quiz.print_stats(all=True)


if __name__ == '__main__':
    main()

# Link to the public GitHub repo tha contains my work from Part 3:
# https://github.com/viliusddd/turing/wargame
