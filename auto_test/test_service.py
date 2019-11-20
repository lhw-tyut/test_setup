import httplib
import uuid
import os
import sys
import simplejson
import time
import tenacity
from do_data import Database_test

REST_SERVER = '13.13.13.33'
REST_SERVER_PORT = 7070


def read_file(f_name):
    with open(f_name, "r") as fp:
        return fp.readline()


def checkout(task, id, ip):
    @tenacity.retry(wait=tenacity.wait_fixed(2))
    def _checkout():
        with Database_test() as data_t:
            res = data_t.select_attr(task, id)
            if res == "0":
                raise
            else:
                return res

    res = _checkout()
    if res != "failed":
        return res
    else:
        print("%s execute task %s failed" % (ip, task))


class RestException(Exception):
    pass


class RestRequest(object):
    def __init__(self, host, port, create_id):
        self.host = host
        self.port = port
        self.create_id = create_id
        self.callbackuri = 'http://%s:%s/task/callback' % (REST_SERVER,
                                                           REST_SERVER_PORT)
        self.headers = self._build_header()

    def _build_header(self):
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json",
                   "taskuuid": self.create_id,
                   "callbackuri": self.callbackuri}
        return headers

    def _send_request(self, uri, method, body, token):
        if not uri:
            raise RestException("uri is required!")

        conn = None
        try:
            conn = httplib.HTTPConnection(self.host, self.port)
            if token:
                self.headers["step"] = token
            conn.request(method, uri, body, self.headers)
            print(self.headers)
            response = conn.getresponse()
            status = response.status
            result = response.read()
        except Exception, e:
            print
            "Exception: %s" % e
            raise e
        finally:
            print(self.headers)
            if conn:
                conn.close()

        return status, result

    def get(self, uri, body=None, token=None):
        return self._send_request(uri, "GET", body, token)

    def post(self, uri, body, token):
        return self._send_request(uri, "POST", body, token)

    def put(self, uri, body, token):
        return self._send_request(uri, "PUT", body, token)

    def delete(self, uri, body, token):
        return self._send_request(uri, "DELETE", body, token)


def ipmi_stop(req, ipmi_ip, username, password):
    path = '/baremetal/ipmi/stop'
    body = [
        {
            "ip": ipmi_ip,
            "username": username,
            "password": password
        }
    ]
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, "poweroff_s")


def ipmi_start(req, ipmi_ip, username, password, mode):
    path = '/baremetal/ipmi/start'
    body = [
        {
            "ip": ipmi_ip,
            "username": username,
            "password": password,
            "mode": mode
        }
    ]
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, "poweron_s")


def ipmi_reset(req, ipmi_ip, username, password):
    path = '/baremetal/ipmi/reset'
    body = [
        {
            "ip": ipmi_ip,
            "username": username,
            "password": password,
        }
    ]
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, "powerreset_s")


def init_image(req, mac, ip):
    path = '/pxe/baremetal/image/init'
    body = {
        "uuid": str(uuid.uuid4()),
        "hostname": "baremetal",
        "username": "root",
        "password": "cds-china",
        "os_type": "centos7",
        "enable_monitor": True,
        "networks": {
            "interfaces": [
                {
                    "mac": mac,
                    "ipaddr": ip,
                    "netmask": "255.255.255.0",
                    "dns": ["114.114.114.114", "114.114.115.115"]
                }
            ],
            "bonds": [
            ],
            "vlans": [
            ],
            "dns": [
                "114.114.114.114",
                "114.114.115.115"
            ]
        }
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, "init_s")


def clone_image(req):
    path = '/pxe/baremetal/image/clone'
    body = {
        "os_version": "ubuntu16_test_64"
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, "clone_s")


def get_hardware_info(req):
    hostinfo = []
    path = "/pxe/baremetal/hardwareinfo"
    (status, result) = req.get(path, None, "get_hwinfo_s")
    hardinfo = simplejson.loads(result)

    host_uuid = str(uuid.uuid4())
    hostinfo.append(host_uuid)

    ip = hardinfo["bmc_address"]
    hostinfo.append(ip)

    for i in hardinfo["net_info"]:
        hostinfo.append(i["mac_address"])

    with Database_test() as data_t:
        data_t.insert_host(hostinfo)
    print(hostinfo)


def create_bms(*attr):

    username = "admin"
    password = "admin"
    ip = attr[0]
    mac = "6c:92:bf:62:ab:9e"
    mode = "uefi"

    with Database_test() as data_t:
        create_id = data_t.select_create_id(ip)
        if create_id:
            create_uuid = create_id[0]
        else:
            create_uuid = str(uuid.uuid4())
            data_t.insert(create_uuid, ip)

    rest = RestRequest("localhost", "7081", create_uuid)
    ipmi_stop(rest, ip, username, password)
    checkout("poweroff_s", create_uuid, ip)
    time.sleep(2)

    ipmi_start(rest, ip, username, password, mode)
    # get dhcpIP from client service
    checkout("poweron_s", create_uuid, ip)

    print("starting service for pxe")
    ipaddress = checkout("dhcp_ip", create_uuid, ip)
    print(ipaddress)
    time.sleep(1)
    rest_pxe = RestRequest(ipaddress, "80", create_uuid)
    print("=====")
    clone_image(rest_pxe)

    # start clone image, get callback
    checkout("clone_s", create_uuid, ip)
    time.sleep(1)

    init_image(rest_pxe, mac, ipaddress)
    checkout("init_s", create_uuid, ip)
    time.sleep(1)

    # reset service
    ipmi_reset(rest, ip, username, password)
    checkout("powerreset_s", create_uuid, ip)


def get_hardinfo(*attr):

    ipaddress = attr[0]
    rest_pxe = RestRequest(ipaddress, "80", "1234")
    print("=====")
    get_hardware_info(rest_pxe)

def boot_deploy_image(*attr):
    create_uuid = "1234"
    rest = RestRequest("localhost", "7081", create_uuid)

    username = "admin"
    password = "admin"
    ip = attr[0]
    mode = "uefi"

    with Database_test() as data_t:
        if not data_t.select_create_id(ip):
            data_t.insert(create_uuid, ip)

    ipmi_stop(rest, ip, username, password)
    time.sleep(5)

    ipmi_start(rest, ip, username, password, mode)
    # get dhcpIP from client service

