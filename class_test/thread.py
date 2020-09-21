import threading
import random
import time

class MyThread(threading.Thread):

    def __init__(self, func, args=None):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


def get_server_info(pods, func, *args):
    tasks = []
    res = {}
    for i in pods:
        t = MyThread(func, args=(i[0], i[1], args[0]))
        tasks.append(t)
        time.sleep(random.uniform(0, 0.3))
        t.start()

    for t in tasks:
        t.join()
        res.update(t.get_result())

    return res
