import logging
import sys


def query_yes_no(question, default='yes'):
    '''
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    '''
    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(
                "Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n"
            )


def logger(filename):
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
