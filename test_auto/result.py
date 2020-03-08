# -*- coding:utf-8 -*-
import os
from database import Database_test

if os.path.exists('pxe_log') and os.path.exists('image_log') and os.path.exists('host_ip'):
    os.remove('pxe_log')
    os.remove('image_log')
    os.remove('host_ip')


with Database_test() as data_t:
    count = data_t.nic_count
    hosts1 = data_t.select_info('host_conf', '*')
    hosts2 = data_t.select_info('host', '*')

tem1 = [i[0] for i in hosts1]
pxe_success = [i[0] for i in hosts2]
pxe_failed = [i for i in tem1 if i not in pxe_success]
install_success = [i[0] for i in hosts2 if 'success' in i]
install_failed = [i for i in pxe_success if i not in install_success]
host_ip = [i for i in hosts1 if i[0] in install_success]

with open('pxe_log', 'a') as fp:
    for i in pxe_failed:
        fp.write("%s pxe boot error\n" % i)
    for i in pxe_success:
        fp.write("%s pxe boot success\n" % i)

with open('image_log', 'a') as fp:
    for i in install_failed:
        fp.write("%s install image error\n" % i)

    for i in install_success:
        fp.write("%s install image success\n" % i)

with open('host_ip', 'a') as fp:
    acount = 0
    for i in host_ip:
        acount += 1
        for j in range(1, count + 1):
            fp.write(i[j])
            if j != count:
                fp.write(' ')
        fp.write('\n')
