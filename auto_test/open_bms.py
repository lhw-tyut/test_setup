import threading
import time
import tenacity
from do_data import Database_test
from test_service import create_bms, read_file, get_hardinfo, boot_deploy_image

def get_host_ips():

    with Database_test() as data_t:
        return data_t.select()

def database_create():
    with Database_test() as data_t:
        data_t.create()
        data_t.create_host()
        data_t.create_dhcpinfo()


def create_bms_task():
    host_ips = get_host_ips()
    print(host_ips)

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

def checkout(host_ips):
    @tenacity.retry(wait=tenacity.wait_fixed(10))
    def _count():
        with Database_test() as data_t:
            res = data_t.select_dhcp_ip()
        if len(host_ips) != res[0]:
            raise
        else:
            with Database_test() as data_t:
                res = data_t.select_dhcp_ip()
            return res

    dhcp_ips = _count()
    return dhcp_ips


def get_hardinfo_task():
    host_ips = ["10.177.178.86"]
    threads = []
    for i in host_ips:
        thread = threading.Thread(target=boot_deploy_image, args=(i,))
        threads.append(thread)

    print("start", time.ctime())

    for i in range(len(host_ips)):
        threads[i].start()
        time.sleep(0.01)

    for i in range(len(host_ips)):
        threads[i].join()

    dhcp_ips = checkout(host_ips)

    threads = []
    for i in dhcp_ips:
        thread = threading.Thread(target=get_hardinfo, args=(i[0],))
        threads.append(thread)

    for i in range(len(host_ips)):
        threads[i].start()
        time.sleep(0.01)

    for i in range(len(host_ips)):
        threads[i].join()

    print("end", time.ctime())


if __name__ == '__main__':
    create_bms_task()
    get_hardinfo_task()
