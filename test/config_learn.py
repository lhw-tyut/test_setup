from configparser import ConfigParser

def config():
    cp1 = ConfigParser()
    cp2 = ConfigParser()
    cp1.read("test/config_file/mysql1.cfg")
    cp2.read("test/config_file/mysql2.ini")

    cp1.get("mysql", "host")
    cp2.get("mysql", "host")

    cp1.get("mysql", "host_one")
    cp2.get("mysql", "host_one")
