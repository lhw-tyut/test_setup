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

    def create(self):
        sql = "create table create_bms " \
              "(create_id varchar(50) primary key, dhcp_ip varchar(30), " \
              "poweron_status varchar(10))"
        self.cursor.execute(sql)

    def insert(self):
        sql = "insert into create_bms " \
              "(create_id, dhcp_ip, poweron_status) " \
              "values ( '{}', \'10.177.178.243', \'success')".format(
              str(uuid.uuid4()))
        self.cursor.execute(sql)

    def update(self, attr, value, pk):
        sql = "update create_bms " \
              "set %s='%s' " \
              "where create_id='%s'" % \
              (attr, value, pk)
        self.cursor.execute(sql)

    def select(self):
        sql = "select * from create_bms"
        self.cursor.execute(sql)
        value = self.cursor.fetchall()
        #for i in value[0]:
        #    print(i)
        print(value)


if __name__ == '__main__':
    with Database_test() as data_t:
        #data_t.insert()
        data_t.select()
        data_t.update('dhcp_ip', "10.177.178.100", "d4511a11-6570-43ab-8e98-8a488086b892")
        data_t.select()
