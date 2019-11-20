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
              "mac3 varchar(20), mac4 varchar(20), mac5 varchar(20), mac6 varchar(20))"
        self.cursor.execute(sql)

    def insert_host(self, attr):
        temp = len(attr)
        attr1 = attr
        if temp != 8:
            for i in range(8-temp):
                attr1.append("0")

        sql = "insert into host " \
              "(create_id, ipmi_ip, mac1, mac2, mac3, mac4) " \
              "values (?, ?, ?, ?, ?, ?, ?, ?)"
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

    # update create_bms table
    def update(self, attr, value, pk):
        sql = "update create_bms " \
              "set %s='%s' " \
              "where create_id='%s'" % \
              (attr, value, pk)
        self.cursor.execute(sql)

    def select(self):
        sql = "select * from host"
        self.cursor.execute(sql)
        value = self.cursor.fetchall()
        res = [i[1] for i in value]
        print(res)
        return res

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
        print(value[0])
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