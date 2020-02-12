import threading
from concurrent.futures import ThreadPoolExecutor
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

    if "centos" in os_version:
        with Database_test() as data_t:
            data_t.delete_dhcpinfo()
            if len(ips) != data_t.select_host_conf_count()[0]:
                for ip in ips:
                    temp = ip.split('\n')[0]
                    res = temp.split()
                    try:
                        data_t.insert_host_conf(res)
                    except:
                        continue

        with Database_test() as data_t:
            tem1 = data_t.select_ipmi_ips()
            tem2 = data_t.select_host_ip()
            return [i for i in tem1 if i not in tem2]
    else:
        return [i.split('\n')[0] for i in ips]


def create_bms_task():
    host_ips = get_host_ips()

    print("start", time.ctime())

    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in host_ips:
            time.sleep(0.1)
            executor.submit(create_bms, i)

    print("end", time.ctime())

def checkout(host_ips):
    @tenacity.retry(wait=tenacity.wait_fixed(10), stop=tenacity.stop_after_delay(600))
    def _count():
        with Database_test() as data_t:
            res = data_t.select_dhcpip_count()
        if len(host_ips) != res[0]:
            raise
        else:
            with Database_test() as data_t:
                res = data_t.select_dhcp_ip()
            return res
    try:
        dhcp_ips = _count()
    except:
        with Database_test() as data_t:
            res = data_t.select_dhcp_ip()
        dhcp_ips = res
    return dhcp_ips


def get_hardinfo_task(os_version):
    host_ips = get_ipmi_ips(os_version)

    print("start", time.ctime())
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in host_ips:
            time.sleep(1)
            executor.submit(boot_deploy_image, i)

    dhcp_ips = checkout(host_ips)

    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in dhcp_ips:
            time.sleep(0.1)
            executor.submit(get_hardinfo, i[0])



    print("end", time.ctime())
    time.sleep(5)

if __name__ == '__main__':
    # set ipmi username password
    os_version = cp.get('image', 'os_version')

    get_hardinfo_task(os_version)
    create_bms_task()
