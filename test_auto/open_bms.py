# -*- coding:utf-8 -*-
import time
from concurrent.futures import ThreadPoolExecutor
from database import Database_test
from service import create_bms, read_file
from service import get_hardinfo, boot_deploy_image

from configparser import ConfigParser

cp = ConfigParser()
cp.read("bms.ini")


def get_host_ips():
    with Database_test() as data_t:
        res = data_t.select()
        for i in res:
            if i[-1] == "failed":
                data_t.delete_info(ip=i[0])
        return res


def get_ipmi_ips(os_version):
    with open('ipmi_ips', 'r') as fp:
        ips = fp.readlines()

    if "centos" in os_version:
        with Database_test() as data_t:
            data_t.delete_info()
            if len(ips) != data_t.select_info('host_conf', 'count(*)')[0]:
                for ip in ips:
                    temp = ip.split('\n')[0]
                    res = temp.split()
                    try:
                        data_t.insert_info('host_conf', res)
                    except:
                        continue

        with Database_test() as data_t:
            tem1 = data_t.select_info('host_conf', 'ipmi_ip')
            tem2 = data_t.select_info('host', 'ipmi_ip')
            return [i[0] for i in tem1 if i not in tem2]
    else:
        return [i.split('\n')[0] for i in ips]


def create_bms_task():
    host_ips = get_host_ips()

    print("start", time.ctime())

    with ThreadPoolExecutor(max_workers=50) as executor:
        for i in host_ips:
            time.sleep(0.1)
            executor.submit(create_bms, i)

    print("end", time.ctime())


def get_hardinfo_task(os_version):
    host_ips = get_ipmi_ips(os_version)

    print("start", time.ctime())
    with ThreadPoolExecutor(max_workers=50) as executor:
        for i in host_ips:
            time.sleep(1)
            executor.submit(boot_deploy_image, i)

    print("end", time.ctime())
    time.sleep(5)


if __name__ == '__main__':
    # set ipmi username password
    os_version = cp.get('image', 'os_version')

    get_hardinfo_task(os_version)
    create_bms_task()
