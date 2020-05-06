from functools import reduce
a = [{"username": "usera", "ip": "10.177.178.86", "password": "admin"},
     {"username": "usera", "ip": "10.177.178.86", "password": "admin", "aa": 'a'}]


def list_dict_duplicate_removal():
    data_list = [{"username": "usera", "ip": "10.177.178.86", "password": "admin"},
         {"username": "usera", "ip": "10.177.178.86", "password": "admin", "aa": 'a'}]
    run_function = lambda x, y: x if y in x else x + [y]
    data = reduce(run_function, [[], ] + data_list)
    return reduce(run_function, [[], ] + data_list)


if __name__ == '__main__':
    print(list_dict_duplicate_removal())

