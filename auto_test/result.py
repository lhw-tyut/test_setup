from DataBase import Database_test
import os

os.remove('res_pxeboot')
os.remove('res_install_image')


with Database_test() as data_t:
    tem1 = data_t.select_ipmi_ips()
    tem2 = data_t.select_host_ip()
    tem = [i[0] for i in tem1 if i not in tem2]
    tem3 = data_t.select()

with open('res_pxeboot', 'a') as fp:
    for i in tem:
        fp.write("ipmi_ip:%s pxe boot failed" % i)

with open('res_install_image', 'a') as fp:
    for i in tem:
        fp.write("ipmi_ip:%s install test image failed" % i)

    for i in tem3:
        fp.write("ipmi_ip:%s install test image failed" % i)
