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
    print(a2)

    b1 = cp1.get("mysql", "host_one")
    print(b1)
    b2 = cp2.get("mysql", "host_one")
    print(b2)

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

config()