import threading
import time
import tenacity
from DataBase import Database_test
from Service import create_bms, read_file, get_hardinfo, boot_deploy_image

def get_host_ips():
    with Database_test() as data_t:
        res = data_t.select()
        for i in res:
            if i[-1] == "failed":
                data_t.delete_create_bms(i[1])
        return res

def get_ipmi_ips():
    with open("ipmi_ips", 'r') as fp:
        return fp.readlines()


def create_bms_task():
    host_ips = get_host_ips()

    threads = []
    for i in host_ips:
        thread = threading.Thread(target=create_bms, args=i)
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
            res = data_t.select_dhcp_count()
        if len(host_ips) != res[0]:
            raise
        else:
            with Database_test() as data_t:
                res = data_t.select_dhcp_ip()
            return res

    dhcp_ips = _count()
    return dhcp_ips


def get_hardinfo_task():
    host_ips = get_ipmi_ips()
    threads = []
    for i in host_ips:
        ip = i.split("\n")[0]
        thread = threading.Thread(target=boot_deploy_image, args=(ip,))
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
    get_hardinfo_task()
    create_bms_task()

