from quiz import Quiz
from tools.data import Data


def test_split_question_ids():
    data = Data(filename='test_db.csv')
    quiz = Quiz(qids='1', data=data)
    assert quiz._split_question_ids() == [1]

    quiz = Quiz(qids='1-4', data=data)
    assert quiz._split_question_ids() == [1, 2, 3, 4]

    quiz = Quiz(qids='1,4', data=data)
    assert quiz._split_question_ids() == [1, 4]

def test_get_questions_index():
    data = Data(filename='test_db.csv')
    quiz = Quiz(qids='1', data=data)
    assert quiz._get_questions_index() == [0]

    quiz = Quiz(qids='1-3', data=data)
    assert quiz._get_questions_index() == [0, 1, 2]

    quiz = Quiz(qids='1,3,4', data=data)
    assert quiz._get_questions_index() == [0, 2, 3]

def test_disable():
    data = Data(filename='test_db.csv')
    quiz = Quiz(qids='1,3,4', data=data)
    assert quiz.disable() is None

def test_reset_all():
    data = Data(filename='test_db.csv')
    quiz = Quiz(qids='1-4', data=data)
    assert quiz.reset_all() is None