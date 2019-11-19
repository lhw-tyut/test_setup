import threading
import time
from .do_data import Database_test
from .test_service import create_bms

with Database_test() as data_t:
    host_ips = data_t.select()


if __name__ == '__main__':
    threads = []
    for i in host_ips:
        thread = threading.Thread(target=create_bms, args=(i,))
        threads.append(thread)

    print("start", time.ctime())

    for i in range(len(host_ips)):
        threads[i].start()
        time.sleep(0.01)

    for i in range(len(host_ips)):
        threads[i].join()

    print("end", time.ctime())


