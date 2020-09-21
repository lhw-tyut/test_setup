# -*- coding:utf-8 -*-
# import multiprocessing
# import timeit
# import operator
# import threading
# import re
#
# partter = re.compile(r'\w{4}-\w{4}-\w{4}')
#
# datas = '''
# result:
# Flags: * - Backup
#        # - forwarding logical interface, operations cannot be performed based
#            on the interface.
# BD   : bridge-domain   Age : dynamic MAC learned time in seconds
# -------------------------------------------------------------------------------
# MAC Address    VLAN/VSI/BD   Learned-From        Type                Age
# -------------------------------------------------------------------------------
# b496-9132-2ea1 1799/-/-      10GE2/0/6           dynamic              86
# -------------------------------------------------------------------------------
# Total items: 1
# '''
# pattern = re.compile(r'\w{4}-\w{4}-\w{4}')
#
#
# # command = "display mac-address interface %s" % port
# # datas = self._execute_relative(["display mac-address interface %s" % port])
# mac = ""
# for line in datas.split("\n"):
#     data = pattern.findall(line)
#     if data:
#         mac = ":".join(i[0:2] + ":" + i[2:4] for i in data[0].split("-")).upper()
#         break
# if mac == "":
#     print("error")
# print ({"mac": mac})
#
#
# def test(*args, **kwargs):
#     print(args)
#     print(args[0][0])
#     print(kwargs)
#
# test('asfsd', 'b', a="c", b="d")
#
# a = {}
# a.update({"a": 1, "b":2})
# print a
#
# a = '''
# 10GE1/0/9               trunk           1  1 3014
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/10              trunk           1  1 3014 3142
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/11              trunk           1  1 1771
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/12              access       1799  --
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/13              access          1  --
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/14              access          1  --
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/15              access          1  --
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/16              access          1  --
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/17              access          1  --
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/18              access          1  --
#
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
# 10GE1/0/19              access          1  --
#
# Port                    Link Type    PVID  Trunk VLAN List
# -------------------------------------------------------------------------------
#
# '''
#
# # for i in a.split('\n'):
# #     if any([j in i for j in ["Link Type", "-----", "port vlan"]]) or i == "":
# #         continue
# #     else:
# #         print i
#
# res = []
# for line in a.split('\n'):
#
#         info = line.split()
#         port_config = {}
#         vlans = ""
#         if "trunk" in info:
#             vlans = ",".join(info[4:]) if len(info) > 4 else ",".join(info[3:])
#         elif "access" in info:
#             vlans = info[2]
#         else:
#             continue
#         port_config.update({"port": info[0], "link_type": info[1], "vlan": vlans})
#         res.append(port_config)
# print res
#
# # print(len(""))
# #
# # import os
# # os.makedirs()
#
# sn_info = []
# res = """
# MainBoard:
# ESN: 2102350JAR6TJB000053
#
# """
# sns = res.split("\n")
# for line in sns:
#     if "MainBoard" in line:
#         ind = sns.index(line)
#         sn = sns[ind + 1].split(":")[1].strip()
#         sn_info.append({"sn": sn, "type": "master"})
#     if "SlaveBoard" in line:
#         ind = sns.index(line)
#         sn = sns[ind + 1].split(":")[1].strip()
#         sn_info.append({"sn": sn, "type": "slave"})
#     if len(sn_info) == 1:
#         sn_info[0]["type"] = ""
# print({"sn_list": sn_info})
#
# print("".join(["aa", "_", "bb"]))
#
# a = "False"
#
# if a:
#     print(a)
import os
path_file = "http://aaa.aa:111/var/aa"
if os.path.dirname(path_file):
    print(os.path.dirname(path_file))
else:
    print("aaa")


# from concurrent.futures import ThreadPoolExecutor
# import subprocess
#
# def shell_cmd(cmd):
#     process = subprocess.Popen(
#     cmd, bufsize=10000,
#     shell=True,
#     stdout=subprocess.PIPE,
#     stderr=subprocess.PIPE,
#     close_fds=True, executable='/bin/bash')
#
#     (stdout, stderr) = process.communicate()
#     print stdout
#
# def res_return():
#     with ThreadPoolExecutor(max_workers=100) as executor:
#         for host in range(400):
#             executor.submit(shell_cmd, "ls /root/config")

class BaremetalError(Exception):
    message = "An exception occurred"
    suggestion = 'An unexpected error occurred. Please try back later.'
    code = '21000'

    def __init__(self, error_type, **kwargs):
        try:
            if isinstance(error_type, dict):
                self.code = error_type['code']
                self.suggestion = error_type['suggestion']
            else:
                for i in error_type:
                    if kwargs['error'] and i['msg'] in kwargs['error']:
                        self.code = i['code']
                        self.suggestion = i['suggestion']
            self._error_string = "{}:{}".format(self.__class__.__name__, self.message % kwargs)

        except Exception:
            self._error_string = self.message

    def __str__(self):
        return "{},kw{}".format(self._error_string, self.suggestion)

    def __repr__(self):
        """Should look like BaremetalError('message: suggestion')"""
        return "{}:{}".format(self.__class__.__name__, self.__str__())




class ConfigDriveSizeError(BaremetalError):
    message = "baremetal[%(command)s] %(error)s"

SWITCH_MAC_PORT = {'code': '20209', 'msg': 'port-mac does not exist', "suggestion": 'jkk'}

a = ConfigDriveSizeError(SWITCH_MAC_PORT, command="ipmitool -I lanplus", error='port-mac does not exist')
print(a.suggestion)
print(a._error_string)
print(a.code)
print(a.__repr__())

te = '1'
if te == 1:
    print(te)

class Test(object):
    message = "aaa"
    code = 'bbb'
    def __init__(self, a=None, **kwargs):
        print(a)
        print(kwargs)
        self.error = self.message % kwargs
        print(self.error)

class Test1(Test):

    def print_test(self):
        print(hasattr(self, 'code'))

# test = Test1('aaa',bb='123', cc='456')
# NFS_MOUNT_ERROR = {'code': '20501', 'msg': 'mount.nfs: Connection refused', 'suggestion': "请检查pxe配置文件是否正确或管理节点内网IP能否连通"}
# COPY_IMAGE_ERROR = {'code': '20502', 'msg': 'copy to client failed', 'suggestion': "请检查镜像文件是否存在"}
# CONVERT_IMAGE_ERROR = {'code': '20503', 'msg': 'Device is too small', 'suggestion': "克隆镜像失败，镜像模板分区超出磁盘实际大小"}
# CHECKSUM_ERROR = {'code': '20504', 'msg': 'image checksum is not matched', 'suggestion': "请检查镜像是否被修改"}
# DEVICE_ERROR = {'code': '20505', 'msg': 'could not find suitable device', 'suggestion': "请检查磁盘是否识别，是否需要磁盘raid"}
# PART_MOUNT_ERROR = {'code': '20551', 'msg': 'special device None does not exist', 'suggestion': "请检查镜像是否被正确克隆或分区标签是否正确"}
# EFIBOOTMGR_CMD_ERROR = {'code': '20552', 'msg': 'efibootmgr: command not found',
#                         'suggestion': "该UEFI镜像不符合标准，需要预装efibootmgr命令"}
# GEN_GRUB_CFG_ERROR = {'code': '20553', 'msg': '/boot/efi/EFI/Dellcentos/grub.cfg.new: No such file or directory',
#                       'suggestion': "启动分区/boot/efi/EFI下存在未知目录，如centos系统默认为BOOT，centos，请检查"}
# PARTLABEL_ERROR = {'code': '20554', 'msg': 'partition labeled was not found', 'suggestion': "请检查镜像是否被正确克隆或分区标签是否正确"}
#
# CLEAN_NET_ERROR = {'code': '20601', 'msg': 'clean net config failed', 'suggestion': "请检查系统类型os_type参数是否正确"}
# CLEAN_WIN_NET_ERROR = {'code': '20602', 'msg': 'the system of windows is not support temporarily',
#                        'suggestion': "Windows系统不支持网络配置清除"}

test1 = Test1()
test1.print_test()
