import threading
import time
import tenacity
from DataBase import Database_test
from Service import create_bms, read_file, get_hardinfo, boot_deploy_image

from configparser import ConfigParser

cp = ConfigParser()
cp.read("bms.ini")

def get_host_ips():
    with Database_test() as data_t:
        res = data_t.select()
        for i in res:
            if i[-1] == "failed":
                data_t.delete_create_bms(i[1])
        return res

def get_ipmi_ips(os_version):

    with open('ipmi_ips', 'r') as fp:
        ips = fp.readlines()

    if "ubuntu" in os_version:
        with Database_test() as data_t:
            data_t.create_host_conf()
            for ip in ips:
                temp = ip.split('\n')[0]
                res = temp.split(' ')
                data_t.insert_host_conf(res)

        with Database_test() as data_t:
            tem = data_t.select_ipmi_ips()
            return [i[0] for i in tem]
    else:
        return [i.split('\n')[0] for i in ips]


def create_bms_task(ipmi_info, os_version):
    host_ips = get_host_ips()

    threads = []
    for i in host_ips:
        thread = threading.Thread(target=create_bms, args=(i, ipmi_info, os_version))
        threads.append(thread)

    print("start", time.ctime())

    for i in range(len(host_ips)):
        threads[i].start()
        time.sleep(0.01)

    for i in range(len(host_ips)):
        threads[i].join()

    print("end", time.ctime())

def checkout(host_ips):
    @tenacity.retry(wait=tenacity.wait_fixed(10), stop=tenacity.stop_after_delay(240))
    def _count():
        with Database_test() as data_t:
            res = data_t.select_dhcpip_count()
        if len(host_ips) != res[0]:
            raise
        else:
            with Database_test() as data_t:
                res = data_t.select_dhcp_ip()
            return res

    dhcp_ips = _count()
    return dhcp_ips


def get_hardinfo_task(os_version, ipmi_info):
    host_ips = get_ipmi_ips(os_version)
    threads = []
    for i in host_ips:
        thread = threading.Thread(target=boot_deploy_image, args=(i, ipmi_info))
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
    # set ipmi username password
    ipmi_info = (cp.get('ipmi', 'username'), cp.get('ipmi', 'password'))
    os_version = cp.get('image', 'os_version')        # vm_esxi_64    ubuntu16_64

    get_hardinfo_task(os_version, ipmi_info)
    create_bms_task(ipmi_info, os_version)