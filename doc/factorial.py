# built in factorial
from math import factorial as factorialMath

# recursive
def factorialRecursive(n):
    if n == 0:
        return 1
    elif n == 1:
        return n
    else:
        return n*factorialRecursive(n-1)

# sequential
def factorialSequential(n):
    if n == 0:
        return 1
    res = 1
    for k in xrange(2, n+1):
        res *= k
    return res

if __name__ == '__main__':
    from matrix2latex import matrix2latex
    
    N = range(0, 10)
    table = list()
    for func in (factorialMath,
                 factorialRecursive,
                 factorialSequential):
        row = list()
        for n in N:
            res = func(n)  # call func
            row.append(res)# append result to row
        table.append(row)  # append row to table

    # convert to string for labeling
    cl = ["${n}$".format(n=n) for n in N]
    # row labels
    rl = ['$n$', 'Built-in', 'Recursive', 'Sequential']
    caption = '''Vertifying that the different factorial
    implementations gives the same results'''
    matrix2latex(table, 'facV', caption=caption,
                 columnLabels=cl, rowLabels=rl,
                 alignment='r')

    import timeit
    table = list()
    for func in ('factorialMath',
                 'factorialRecursive',
                 'factorialSequential'):
        row = list()
        for n in N:
            statement = 'factorial.{func}({n})'.format(func=func,
                                                       n=n)
            setup = 'import factorial'
            # measure time
            res = timeit.repeat(statement, setup)
            row.append(min(res)) # append result
        table.append(row) # append row to table

    # convert to string for labeling
    cl = ["${n}$".format(n=n) for n in N]
    rl = ['$n$', 'Built-in [$s$]',
          'Recursive [$s$]', 'Sequential [$s$]']
    caption = '''Comparing execution time for
    the different factorial implementations'''
    matrix2latex(table, 'facT', caption=caption,
                 columnLabels=cl, rowLabels=rl,
                 format='$%.3f$')
