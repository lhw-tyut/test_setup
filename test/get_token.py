from functools import reduce
import json
import os
import requests
a = [{"username": "usera", "ip": "10.177.178.86", "password": "admin"},
     {"username": "usera", "ip": "10.177.178.86", "password": "admin", "aa": 'a'}]


def list_dict_duplicate_removal():
    data_list = [{"username": "usera", "ip": "10.177.178.86", "password": "admin"},
         {"username": "usera", "ip": "10.177.178.86", "password": "admin", "aa": 'a'}]
    input("输入任意键继续")
    run_function = lambda x, y: x if y in x else x + [y]
    print(run_function)
    input("输入任意键继续")


    data = reduce(run_function, [[], ] + data_list)
    return reduce(run_function, [[], ] + data_list)


if __name__ == '__main__':
    input("输入任意键继续")
    print(list_dict_duplicate_removal())
    input("输入任意键继续")
    a = requests.get("http://127.0.0.1:9010/bmsdisk/v1/inquire/task/6eaca078-f261-11ea-b391-1263c8bc5e2f")
    print(a)

