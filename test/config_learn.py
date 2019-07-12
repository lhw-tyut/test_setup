from configparser import ConfigParser
import pkg_resources


def config():
    cp1 = ConfigParser()
    cp2 = ConfigParser()
    cp1.read(pkg_resources.resource_filename("test", "config_file/mysql1.cfg"))
    cp2.read(pkg_resources.resource_filename("test", "config_file/mysql2.ini"))

    a1 = cp1.get("mysql", "host")
    print(a1)
    a2 = cp2.get("mysql", "host")
    print(a1)

    b1 = cp1.get("mysql", "host_one")
    print(b1)
    b2 = cp2.get("mysql", "host_one")
    print(b2)
