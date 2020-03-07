# -*- coding:utf-8 -*-
import sqlite3
from configparser import ConfigParser

cp = ConfigParser()
cp.read("bms.ini")

class Database_test():
    def __init__(self):
        self.nic_count = int(cp.get('network', 'count'))
        self.conn = sqlite3.connect("test.db", timeout=10)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def dynamic_table_attr(self, attr):
        macs = ''
        for i in range(self.nic_count):
            mac = attr.format(i + 1)
            macs += mac
        return macs

    # task execute table
    def create(self):
        sql = "create table create_bms (create_id varchar(50) primary key, ipmi_ip varchar(30), " \
              "dhcp_ip varchar(30), dhcp_mac varchar(20), poweroff_s varchar(20), poweron_s varchar(20), " \
              "clone_s varchar(20), init_s varchar(20), powerreset_s varchar(20))"
        self.cursor.execute(sql)

    def insert(self, uuid, ipmi_ip):
        sql = "insert into create_bms values ( '{}', '{}', 0, 0, 0, 0, 0, 0, 0)".format(uuid, ipmi_ip)
        self.cursor.execute(sql)

    # server hard info table
    def create_host(self):
        macs = self.dynamic_table_attr("mac{} varchar(20), ")
        sql = "create table host (ipmi_ip varchar(30) primary key, " + macs + "result varchar(10))"
        self.cursor.execute(sql)

    # dhcp ip table
    def create_dhcpinfo(self):
        sql = "create table dhcpinfo (ipmi_ip varchar(20) primary key, dhcp_ip varchar(20), mac varchar(30))"
        self.cursor.execute(sql)

    def insert_dhcpinfo(self, ip, dhcp_ip, mac):
        sql = "insert into dhcpinfo values ( '{}', '{}', '{}')".format(ip, dhcp_ip, mac)
        self.cursor.execute(sql)

    # server config table
    def create_host_conf(self):
        ips = self.dynamic_table_attr("ip{} varchar(20), ")
        sql = "create table host_conf (ipmi_ip varchar(20) primary key, " + ips + "hostname varchar(30))"
        self.cursor.execute(sql)

    def insert_info(self, table, attr):
        ips = ''
        for i in range(self.nic_count + 1):
            ip = "?, "
            ips += ip
        sql = "insert into {} values (" + ips + "?)".format(table)
        if table == 'host_conf':
            attr.append("bms")
        else:
            attr.append("0")
        self.cursor.execute(sql, tuple(attr))

    def update_info(self, value, attr=None, pk=None, ip=None):
        if pk:
            sql = "update create_bms set %s='%s' where create_id='%s'" % (attr, value, pk)
        else:
            sql = "update host set result='%s' where ipmi_ip='%s'" % (value, ip)
        self.cursor.execute(sql)

    def select(self):
        sql = "select * from host where result!='success'"
        self.cursor.execute(sql)
        value = self.cursor.fetchall()
        return value

    def delete_info(self, ip=None):
        if ip:
            sql = "delete from create_bms where ipmi_ip='{}'".format(ip)
        else:
            sql = "delete from dhcpinfo"
        self.cursor.execute(sql)

    def select_info(self, table, attr, ipmi_ip=None, create_id=None):
        if ipmi_ip:
            sql = "select {} from {} where ipmi_ip='{}'".format(attr, table, ipmi_ip)
            self.cursor.execute(sql)
            value = self.cursor.fetchone()
        elif create_id:
            sql = "select {} from {} where create_id='{}'".format(attr, table, create_id)
            self.cursor.execute(sql)
            value = self.cursor.fetchone()
        else:
            sql = "select {} from {}".format(attr, table)
            self.cursor.execute(sql)
            value = self.cursor.fetchall()
        return value
