from configparser import ConfigParser
import pkg_resources


def config():
    cp1 = ConfigParser()
    cp2 = ConfigParser()
    cp1.read(pkg_resources.resource_filename("test", "config_file/mysql1.cfg"))
    cp2.read(pkg_resources.resource_filename("test", "config_file/mysql2.ini"))

    cp1.get("mysql", "host")
    cp2.get("mysql", "host")

    cp1.get("mysql", "host_one")
    cp2.get("mysql", "host_one")