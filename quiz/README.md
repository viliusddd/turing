Interactive learning tool that allows users to create, practice,
and test their knowledge using multiple-choice and freeform text
questions. The program will track user statistics and provide
options to manage the questions.

```bash
Usage:
  quiz.py (test|practice|question|stats|reset) [--db=<db_file>] [--results=<file>]
  quiz.py test [--limit=<amount>] [--mode=<mode>]
  quiz.py practice [--mode=<mode>]
  quiz.py question (stats|toggle|enable|disable|update|remove|reset) <id>
  quiz.py question (reset-all|add)

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
  reset                 Remove all questions.

Options:
  -h --help             Show this screen.
  --results=<file>      Change testresults filepath. [default: results.txt]
  --db=<db_file>        Change db filepath.

Test and Practice:
  -l --limit=<amount>   Number of test questions to run. [default: 5].
  -m --mode=<mode>      One of modes: freeform, quiz or mixed. [default: mixed].

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
  reset                 Reset question(s) statistics.

Arguments:
  <id>                  Existing dd of question from the database/csv.
```