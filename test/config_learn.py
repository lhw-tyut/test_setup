bios_set = ''
func = ''
def execute_bios_cmd(func, username, password, ip):
    args = ['sh', bios_set, func, username, password]
    args.append("--ipaddr={}".format(ip))
    pass


def test(i):
    key, value = i.items()[0]
    print(''.join([str(i) for i in i.items()[0]]))
test({'a':1})


print("sdfg %s", "df")

class AgentResponse(object):
    def __init__(self, success=True, error=None):
        self.success = success
        self.error = error if error else ''


class SetSwitchResponse(AgentResponse):
    def __init__(self):
        super(SetSwitchResponse, self).__init__()

rsp = SetSwitchResponse()
rsp.data = "aaaa"

print(rsp.__dict__)
print(rsp.data)

import jsonobject
ip_info = jsonobject.loads({"username": "body.adminname", "password": "body.adminpassword", "ip": "body.ip"})
print(ip_info)