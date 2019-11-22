import multiprocessing
import timeit
import operator
import threading

# a = []
# if a:
#     print(a)

# def test(attrs = None):
#     if attrs:
#         for i in attrs:
#             print(i)
#     else:
#         print('is NULL')
#
# test([])
#
# with open("aa.txt", 'r') as fp:
#     res = fp.readlines()
#     for i in res:
#         print(i.split("\n")[0])

# def test(*att, **attr):
#     # for i in attr:
#     #     print(i)
#     print(attr)
#     print(att)
#     print(attr['os'])
#     print(attr['t'])
# a = "centos"
# b = [1,2,4]
# ip = ("aa", "bb", "cc")
#
# threads = []
# for i in range(2):
#     t = threading.Thread(target=test, args=(ip, a, b), kwargs={'ip':ip, 'os': a, 't':b})
#     threads.append(t)
#
# for th in threads:
#     th.start()

a = 'aaa'
b = a.split('\n')
print(b)