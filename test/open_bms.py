import threading
import time
import os
from do_data import Database_test
from test_service import create_bms, read_file, get_hardinfo

def get_host_ips():

    with Database_test() as data_t:
        return data_t.select()


if __name__ == '__main__':
    host_ips = get_host_ips()
    print(host_ips)

    threads = []
    for i in host_ips:
        thread = threading.Thread(target=get_hardinfo, args=(i,))
        threads.append(thread)

    print("start", time.ctime())

    for i in range(len(host_ips)):
        threads[i].start()
        time.sleep(0.01)

    for i in range(len(host_ips)):
        threads[i].join()

    print("end", time.ctime())
