#! .venv/bin/python
'''
TODO: Interactive learning tool that allows users to create, practice,
and test their knowledge using multiple-choice and freeform text
questions. The program will track user statistics and provide
options to manage the questions.

Usage:
  ./quiz.py [options]
  ./quiz.py test|practice|question|status
  ./quiz.py test
  ./quiz.py practice
  ./quiz.py profile [<username>|--user=<username>|--add-user=<username>|--remove-user=<username>]
  ./quiz.py question [<id>|--toggle-status <id>|--remove <id>]
  ./quiz.py status [--id=<id>|--user=<username>] [--status=<status> --type=<type>]


Commands:
  test              Test mode
  practice          Practice mode
  question          Questions editing mode
  status            Show statistics of questions
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
  --status          Choose to show only active or inactive questions
  --type            Choose to show free-form or multi-choice questions
'''

import csv
import random

from docopt import docopt
from tabulate import tabulate


def get_db(filename):
    with open(filename) as file:
        reader = list(csv.DictReader(file))
        for row in reader:
            row['id'] = int(row['id'])
            row['times_shown'] = int(row['times_shown'])
            row['correct'] = int(row['correct'])

    return reader


def append_db(row, filename='db1_short.csv'):
    # generate header
    with open(filename) as file:
        header = list(file)[0]
        print('header: ', header)

    with open(filename, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)

        print(row)
        writer.writerow(row)


def save_db(db: list, filename='db1_short.csv'):
    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=[i for i in db[0]])
        writer.writeheader()
        writer.writerows(db)


def freeform_question(db):
    for i, row in enumerate(db):
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

    save_db(db)
    # print(db)


def quiz_question(db):
    abc = ['A', 'B', 'C', 'D']

    for i, row in enumerate(db):
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

    save_db(db)


def add_question(db, question):
    # question;multiple_choices;correct_answer
    # if multipple_choices is omited, then it will be treated as
    # free-form question instead of quiz with multiple choices

    # free-form example: Capital of Poland;;Warsaw
    # quiz example: Capital of Poland;Vilnius, Riga, Kiev;Warsaw

    template = {
        'id': max([row['id'] for row in db]) + 1,
        'status': 'active',
        'question': '',
        'choices': '',
        'answer': '',
        'times_shown': 0,
        'correct': 0,
    }

    question = question.split(';')

    template['question'] = question[0]
    template['choices'] = question[1]
    template['answer'] = question[2]

    db.append(template)
    save_db(db)


def status(db):
    """
    Show grid with questions and their status
    """

    for row in db:
        if row['choices']:
            row['type'] = 'multi-choice'
        else:
            row['type'] = 'free-form'

        del row['answer']
        del row['choices']

        if row['correct'] == 0:
            row['correct'] = '0%'
        else:
            row['correct'] = \
                f'{row["times_shown"] / row["correct"] * 100}%'

    # print(tabulate(db, headers='keys', tablefmt="rounded_outline"))
    return tabulate(
        db,
        headers='keys',
        tablefmt='rounded_grid',
        colalign=('right', 'center', 'left', 'left', 'left', 'center')
    )


def args():
    pass


def main():
    db = get_db('db1_short.csv')
    # print(db)

    # freeform_question(db)
    # quiz_question(db)

    # a = input('question: ')
    # add_question(db, a)

    print(status(db))


if __name__ == '__main__':
    main()

# Link to the public GitHub repo tha contains my work from Part 3:
# TODO: https://github.com/viliusddd/turing/quiz
