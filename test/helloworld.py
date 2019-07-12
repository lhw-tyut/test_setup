# !/usr/bin/env python
# -*- coding:utf-8 -*-
import random

def print_hello_world():
    print("hello world")

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
