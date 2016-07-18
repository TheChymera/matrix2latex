import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.expanduser(__file__)))

f = open(os.path.join(SCRIPT_DIR, 'test.tex'))
answers = dict()
for line in f:
    if line.startswith('%%%'):
        name = line[3:-1]               # ignore %%% and \n
        answers[name] = ''
    else:
        answers[name] += line
f.close()


def loopTwoLists(x, y):
    for ix in range(max([len(x), len(y)])):
        try: a = x[ix].strip()
        except: a = ''
        try: b = y[ix].strip()
        except: b = ''
        yield a, b

def assertEqual(x, name):
    # assert each line is equal, ignoring leading and trailing spaces
    print(x)
    y = answers[name]
    x = x.split('\n')
    y = y.split('\n')
    correct = True
    for a, b in loopTwoLists(x, y):
        if a != b:
            correct = False # found 1 or more error
            
    if not(correct):
        for a, b in loopTwoLists(x, y):
            print(a,b)
        raise AssertionError
