with open('ipmi_ips', 'r') as fp:
    ips = fp.readlines()
    for ip in ips:
        temp = ip.split('\n')[0]
        res = temp.split()
        print(res)