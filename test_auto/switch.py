# -*- coding:utf-8 -*-
import simplejson
import xlrd
import time
from configparser import ConfigParser
from service import RestRequest

cp = ConfigParser()
cp.read("bms.ini")

EXCEL_PATH = cp.get("excel", "path")
PXE_VLAN = cp.get('network', 'pxe_vlan')
NIC_COUNT = int(cp.get('network', 'count'))
SW_USERNAME = cp.get('network', 'sw_username')
SW_PASSWORD = cp.get('network', 'sw_password')

def set_vlan(req, ip ,ports):
    path = '/baremetal/switch/vlan/set'
    body = {
        "username": SW_USERNAME,
        "password": SW_PASSWORD,
        "host": ip,
        "ports": ports
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, 'set_vlan')

def unset_vlan(req, ip, ports):
    path = '/baremetal/switch/vlan/unset'
    body = {
        "username": SW_USERNAME,
        "password": SW_PASSWORD,
        "host": ip,
        "ports": ports
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, 'unset_vlan')

def get_switch_port(type):
    switch_index = 11 + NIC_COUNT
    excel_path = EXCEL_PATH
    excel = xlrd.open_workbook(excel_path, encoding_override="utf-8")

    sheets = excel.sheet_names()
    table = excel.sheet_by_name(sheets[0])
    res = {}
    data_port = table.col_values(12)
    for i in range(NIC_COUNT):
        data_ip = table.col_values(switch_index + i)
        data = [[data_port[i], data_ip[i]] for i in range(1, len(data_port))]

        for i in set(data_ip[1:]):
            res[i] = []
        for i in data:
            res[i[1]].append(i[0])
        if type == 'pxe':
            return res
    return res

def pxe_set_vlan(type):
    create_uuid = "1234"
    rest = RestRequest("localhost", "7081", create_uuid)
    res = get_switch_port(type)
    for i in res.keys():
        ip = i
        ports = []
        for j in res[i]:
            port = {
                "port_name": j,
                "vlan_id": [PXE_VLAN],
                "current_link_type": "access",
                "set_link_type": "access"
            }
            ports.append(port)
        set_vlan(rest, ip, ports)
        time.sleep(3)

def pxe_unset_vlan(type):
    create_uuid = "1234"
    rest = RestRequest("localhost", "7081", create_uuid)
    res = get_switch_port(type)
    for i in res.keys():
        ip = i
        ports = []
        for j in res[i]:
            port = {
                "port_name": j,
                "current_link_type": "access"
            }
            ports.append(port)
        unset_vlan(rest, ip, ports)
        time.sleep(3)

pxe_set_vlan('pxe')    # pxe/other
# pxe_unset_vlan('pxe')  # pxe/other