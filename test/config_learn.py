from configparser import ConfigParser
import pkg_resources
import logging
from helloworld import print_hello_world

logging.basicConfig(level=logging.INFO,
         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
         datefmt='[%Y-%m_%d %H:%M:%S]',
         filename='my.log',
         filemode='a')
logger = logging.getLogger(__name__)
print(logger)
def config():

    cp1 = ConfigParser()
    cp2 = ConfigParser()
    cp1.read(pkg_resources.resource_filename("test", "config_file/mysql1.cfg"))
    cp2.read(pkg_resources.resource_filename("test", "config_file/mysql2.ini"))

    a1 = cp1.get("mysql", "host")

    logger.info("starting to get hardware information")
    print(a1)
    a2 = cp2.get("mysql", "host")
    print(a2)

    b1 = cp1.get("mysql", "host_one")
    print(b1)
    b2 = cp2.get("mysql", "host_one")
    print(b2)

    print_hello_world()

# from netmiko import ConnectHandler
#
# cisco_config = {
#     "device_type": "cisco_ios",
#     "username": "sshadmin",
#     "password": "CDS-china1",
#     "ip": "10.177.178.243"
# }
# cmd_set = ["show port-channel usage"]
# conn1 = ConnectHandler(**cisco_config)
# output1 = conn1.send_command("show role | grep ssh")
# print(output1)
# print("-------------======================--------------")
#
# conn1.config_mode()
# output2 = conn1.send_config_set(config_commands=cmd_set)
# print(output2)
#
# huawei_config = {
#     "device_type": "huawei_telnet",
#     "username": "admin123",
#     "password": "CDS-china1",
#     "ip": "10.177.178.241"
# }
#
# conn2 = ConnectHandler(**huawei_config)
# output3 = conn2.send_command("display interface 10GE1/0/3")
# print(output3)
if __name__ == '__main__':
    config()