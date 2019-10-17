import re
aa = '''*    1     6c92.bf62.ab9f   dynamic  0         F      F    Eth1/7
*    1     b859.9fac.1331   dynamic  0         F      F    Eth1/10'''
pattern = re.compile(r'\S+')


for line in aa.split("\n"):
    data = pattern.findall(line)
    mac = ":".join(i[0:2] + ":" + i[2:4] for i in data[2].split("."))
    print(mac)
    print(data[-1])

aa = "{'mac': '6c:92:bf:62:ab:9f', 'ipaddress': '13.13.13.180'}"


ip = ""
if not ip:
    print("true")
