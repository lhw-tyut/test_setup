import httplib
import uuid
import simplejson
import time
import tenacity
from configparser import ConfigParser
from DataBase import Database_test
import logging

logging.basicConfig(level=logging.DEBUG,
         format='%(asctime)s %(levelname)s %(process)d %(name)s.%(lineno)d %(message)s',
         datefmt='[%Y-%m_%d %H:%M:%S]',
         filename='create_bms.log',
         filemode='a')
logger = logging.getLogger(__name__)


cp = ConfigParser()
cp.read("bms.ini")

REST_SERVER = cp.get("rest", "rest_service")
REST_SERVER_PORT = cp.get("rest", "rest_service_port")

def read_file(f_name):
    with open(f_name, "r") as fp:
        return fp.readline()


def checkout(task, id, ip):
    @tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_delay(240))
    def _checkout():
        with Database_test() as data_t:
            res = data_t.select_attr(task, id)
            if res == "0":
                raise
            else:
                return res

    res = _checkout()
    if res != "failed":
        logger.debug("%s execute task %s success" % (ip, task))
        print("%s execute task %s success" % (ip, task))
    else:
        logger.debug("%s execute task %s failed" % (ip, task))
        print("%s execute task %s failed" % (ip, task))

    return res


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
            response = conn.getresponse()
            status = response.status
            result = response.read()
        except Exception, e:
            print
            "Exception: %s" % e
            raise e
        finally:
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


def init_image(req, bonds=[], vlans=[]):
    path = '/pxe/baremetal/image/init'
    body = {
        "uuid": str(uuid.uuid4()),
        "username": cp.get("image", "username"),
        "password": cp.get("image", "password"),
        "os_type": 'linux',
        "networks": {
            "interfaces": [
            ],
            "bonds": bonds,
            "vlans": vlans,
            "dns": [
                "114.114.114.114",
                "114.114.115.115"
            ]
        }
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, "init_s")


def clone_image(req, os_version):
    path = '/pxe/baremetal/image/clone'
    body = {
        "os_version": os_version
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
    logger.debug("get hardware information %s" % hostinfo)

def create_bms(*attr):
    create_uuid = str(uuid.uuid4())
    create_res = []

    username = attr[1][0]
    password = attr[1][1]

    ip = attr[0][1]

    mode = "uefi"
    os_version = attr[2]


    with Database_test() as data_t:
        data_t.insert(create_uuid, ip)

    try:
        rest = RestRequest("localhost", "7081", create_uuid)
        ipmi_stop(rest, ip, username, password)
        create_res.append(checkout("poweroff_s", create_uuid, ip))
        time.sleep(2)

        ipmi_start(rest, ip, username, password, mode)
        # get dhcpIP from client service
        create_res.append(checkout("poweron_s", create_uuid, ip))

        print("starting service for pxe")
        logger.debug("%s starting service for pxe" % ip)
        ipaddress = checkout("dhcp_ip", create_uuid, ip)
        time.sleep(1)

        rest_pxe = RestRequest(ipaddress, "80", create_uuid)

        # start clone image, get callback
        clone_image(rest_pxe, os_version)
        create_res.append(checkout("clone_s", create_uuid, ip))
        time.sleep(1)

        if "ubuntu" in os_version:
            with Database_test() as data_t:
                res = data_t.select_host_conf(ip)
            bonds = [
                {
                    "id": "bond0",
                    "bond_mode": res[4],
                    "bond_nics": [attr[0][2], attr[0][3]]
                },
                {
                    "id": "bond1",
                    "bond_mode": res[9],
                    "bond_nics": [attr[0][4], attr[0][5]]
                }
            ]

            vlans = [
                {
                    "id": "vlan0",
                    "vlan_id": res[3],
                    "vlan_nic": "bond0",
                    "ipaddr": res[0],
                    "netmask": res[2],
                    "gateway": res[1],
                    "dns": ["114.114.114.114", "114.114.115.115"]
                },
                {
                    "id": "vlan1",
                    "vlan_id": res[8],
                    "vlan_nic": "bond1",
                    "ipaddr": res[5],
                    "netmask": res[7],
                    "gateway": res[6],
                    "dns": ["114.114.114.114", "114.114.115.115"]
                }
            ]
            init_image(rest_pxe, bonds, vlans)
            create_res.append(checkout("init_s", create_uuid, ip))
            time.sleep(1)
    except:
        with Database_test() as data_t:
            data_t.update_host("failed", ip)
        raise

    with Database_test() as data_t:
        if "failed" in create_res:
            data_t.update_host("failed", ip)
        else:
            data_t.update_host("success", ip)

    # reset service
    ipmi_reset(rest, ip, username, password)
    checkout("powerreset_s", create_uuid, ip)


def get_hardinfo(*attr):

    ipaddress = attr[0]
    rest_pxe = RestRequest(ipaddress, "80", "1234")
    get_hardware_info(rest_pxe)
    print("%s get hardware info success" % ipaddress)

def boot_deploy_image(*attr):
    create_uuid = "1234"
    rest = RestRequest("localhost", "7081", create_uuid)

    username = attr[1][0]
    password = attr[1][1]
    ip = attr[0]
    mode = "uefi"

    ipmi_stop(rest, ip, username, password)
    logger.debug("%s execute task %s success" % (ip, "power off"))
    print("%s execute task %s success" % (ip, "power off"))
    time.sleep(5)

    ipmi_start(rest, ip, username, password, mode)
    logger.debug("%s execute task %s success" % (ip, "power on"))
    print("%s execute task %s success" % (ip, "power on"))
    logger.debug("%s wait pxe boot" % ip)
    print("%s wait pxe boot" % ip)
    # get dhcpIP from client service