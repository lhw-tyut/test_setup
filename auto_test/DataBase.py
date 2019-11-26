import sqlite3
import uuid


class Database_test():
    def __init__(self):
        self.conn = sqlite3.connect("test.db")
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    # task execute
    def create(self):
        sql = "create table create_bms " \
              "(create_id varchar(50) primary key, ipmi_ip varchar(30), dhcp_ip varchar(30), " \
              "poweroff_s varchar(20), poweron_s varchar(20), clone_s varchar(20)," \
              "init_s varchar(20), powerreset_s varchar(20))"
        self.cursor.execute(sql)

    def insert(self, uuid, ipmi_ip):
        sql = "insert into create_bms " \
              "(create_id, ipmi_ip, dhcp_ip, poweroff_s, poweron_s, clone_s, init_s, powerreset_s) " \
              "values ( '{}', '{}', 0, 0, 0, 0, 0, 0)".format(uuid, ipmi_ip)
        self.cursor.execute(sql)

    # server table
    def create_host(self):
        sql = "create table host " \
              "(create_id varchar(50) primary key, ipmi_ip varchar(30), mac1 varchar(30), mac2 varchar(30), " \
              "mac3 varchar(20), mac4 varchar(20), mac5 varchar(20), mac6 varchar(20), result varchar(10))"
        self.cursor.execute(sql)

    def insert_host(self, attr):
        temp = len(attr)
        attr1 = attr
        if temp != 9:
            for i in range(9-temp):
                attr1.append("0")

        sql = "insert into host " \
              "(create_id, ipmi_ip, mac1, mac2, mac3, mac4, mac5, mac6, result) " \
              "values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(sql, tuple(attr1))

    # dhcpIP table
    def create_dhcpinfo(self):
        sql = "create table dhcpinfo " \
              "(create_id varchar(50) primary key, dhcp_ip varchar(30), mac varchar(30))"
        self.cursor.execute(sql)

    def insert_dhcpinfo(self, dhcp_ip, mac):
        sql = "insert into dhcpinfo " \
              "(create_id, dhcp_ip, mac) " \
              "values ( '{}', '{}', '{}')".format(str(uuid.uuid4()), dhcp_ip, mac)
        self.cursor.execute(sql)

    # server table
    def create_host_conf(self):
        sql = "create table host_conf " \
              "(ipmi_ip varchar(20), ip1 varchar(20), netmask1 varchar(20), " \
              "gateway1 varchar(20), bond_mode varchar(2),ip2 varchar(20), netmask2 varchar(20), " \
              "gateway2 varchar(20), ip3 varchar(20), netmask3 varchar(20), gateway3 varchar(20))"
        self.cursor.execute(sql)

    def insert_host_conf(self, attr):
        sql = "insert into host_conf " \
              "(ipmi_ip, ip1, netmask1, gateway1, bond_mode, " \
              "ip2, netmask2, gateway2, ip3, netmask3, gateway3) " \
              "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(sql, tuple(attr))

    # update create_bms table
    def update_create_bms(self, attr, value, pk):
        sql = "update create_bms " \
              "set %s='%s' " \
              "where create_id='%s'" % \
              (attr, value, pk)
        self.cursor.execute(sql)

    def update_host(self, value, ip):
        sql = "update host " \
              "set result='%s' " \
              "where ipmi_ip='%s'" % \
              (value, ip)
        self.cursor.execute(sql)

    def select(self):
        sql = "select * from host where result!='success'"
        self.cursor.execute(sql)
        value = self.cursor.fetchall()
        return value

    def select_dhcpip_count(self):
        sql = "select count(*) from dhcpinfo"
        self.cursor.execute(sql)
        value = self.cursor.fetchone()
        return value

    def select_dhcp_ip(self):
        sql = "select dhcp_ip from dhcpinfo"
        self.cursor.execute(sql)
        value = self.cursor.fetchall()
        return value

    def select_attr(self, attr, id):
        sql = "select {} from create_bms where create_id='{}'".format(attr, id)
        self.cursor.execute(sql)
        value = self.cursor.fetchone()
        return value[0]

    def select_mac(self, mac):
        sql = "select ipmi_ip, mac1 from host where mac1='{}'".format(mac)
        self.cursor.execute(sql)
        value = self.cursor.fetchone()
        return value

    def select_create_id(self, ip):
        sql = "select create_id from create_bms where ipmi_ip='{}'".format(ip)
        self.cursor.execute(sql)
        value = self.cursor.fetchone()
        return value

    def select_host_conf(self, ip):
        sql = "select ip1, netmask1, gateway1, bond_mode, " \
              "ip2, netmask2, gateway2, ip3, netmask3, gateway3 from host_conf " \
              "where ipmi_ip='{}'".format(ip)
        self.cursor.execute(sql)
        value = self.cursor.fetchone()
        return value

    def select_ipmi_ips(self):
        sql = "select ipmi_ip from host_conf"
        self.cursor.execute(sql)
        value = self.cursor.fetchall()
        return value

    def delete_create_bms(self, ip):
        sql = "delete from create_bms " \
              "where ipmi_ip='{}'".format(ip)
        self.cursor.execute(sql)