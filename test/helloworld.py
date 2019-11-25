# !/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import os
import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG,
         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
         datefmt='[%Y-%m_%d %H:%M:%S]',
         filename='my.log',
         filemode='a')
logger = logging.getLogger(__name__)
print(logger)

def create_bms(*args):
    time.sleep(random.randint(0,6))
    print("No. %s" % args[0])
    logger.debug("No. %s" % args[0])

def print_hello_world():
    threads = []
    for i in range(1000):
        thread = threading.Thread(target=create_bms, args=(i,))
        threads.append(thread)

    print("start", time.ctime())

    for i in range(1000):
        threads[i].start()
        time.sleep(0.01)

    for i in range(1000):
        threads[i].join()

    print("end", time.ctime())

def guess():
    num = random.randint(1,100)
    print("猜猜我心里想什么数")
    while True:
        self_guess = int(input("猜猜我是多少"))

        if self_guess == num:
            print("yes")
            break
        elif self_guess > num:
            print("big")
        else:
            print("little")

# a = "switchport access vlan  30,"
# print(a[:-1])
