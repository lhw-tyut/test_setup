import multiprocessing
import timeit
import operator

# a = []
# if a:
#     print(a)

def test(attrs = None):
    if attrs:
        for i in attrs:
            print(i)
    else:
        print('is NULL')

test([])

with open("aa.txt", 'r') as fp:
    res = fp.readlines()
    for i in res:
        print(i.split("\n")[0])