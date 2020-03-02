a = '10.100.100.'
count = 6
with open('host_ip', 'r') as fp:
    ips = fp.readlines()

for i in range(count):
    ip1 = ips[i][:-1]
    ip2 = a + str(181 + i)
    ip3 = '10.10.10.' + str(1 + i)
    print('%s %s %s' %(ip1, ip2, ip3))