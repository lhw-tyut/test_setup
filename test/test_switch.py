import httplib
import uuid

import simplejson

from baremetal.common import jsonobject

REST_SERVER = 'localhost'
REST_SERVER_PORT = 7081


class RestException(Exception):
    pass

class RestRequest(object):
    def __init__(self):
        self.host = REST_SERVER
        self.port = REST_SERVER_PORT
        self.callbackuri = 'http://%s:%s/debug/result' % (REST_SERVER,
                                                          REST_SERVER_PORT)
        self.headers = self._build_header()

    def _build_header(self):
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json",
                   "taskuuid": str(uuid.uuid4()),
                   "callbackuri": self.callbackuri}
        return headers

    def _send_request(self, uri, method, body, token):
        if not uri:
            raise RestException("uri is required!")

        conn = None
        try:
            conn = httplib.HTTPConnection(self.host, self.port)
            if token:
                self.headers["Cookie"] = token
            conn.request(method, uri, body, self.headers)
            response = conn.getresponse()
            status = response.status
            result = response.read()
        except Exception, e:
            print "Exception: %s" % e
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

username = "admin-ssh"
password = "CDS-china1"
host = "10.177.178.241"


def set_vlan(req):
    path = '/baremetal/switch/vlan/set'
    body = {
        "username": username,
        "password": password,
        "host": host,
        "ports": [
            {
                "port_name": "10GE1/0/13",
                "vlan_id": ["2222", "2225-2233"],
                "current_link_type": "trunk",
                "set_link_type": "trunk"
            }
        ]

    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "set switch result: %s" % result


def unset_vlan(req):
    path = '/baremetal/switch/vlan/unset'
    body = {
        "username": username,
        "password": password,
        "host": host,
        "ports": [
            {
                "port_name": "10GE1/0/13",
                "current_link_type": "access"
            }
        ]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "unset vlan result: %s" % result


def set_limit(req):
    path = '/baremetal/switch/limit/set'
    body = {
        "username": username,
        "password": password,
        "host": host,
        "template_name": "12345678-100",
        "ports": ["10GE1/0/17", "10GE1/0/18"]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "set limit result: %s" % result


def unset_limit(req):
    path = '/baremetal/switch/limit/unset'
    body = {
        "username": username,
        "password": password,
        "host": host,
        "template_name": "12345678-100",
        "ports": ["10GE1/0/11", "10GE1/0/12"]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "unset limit result: %s" % result


def create_limit_template(req):
    path = '/baremetal/switch/limit/create'
    body = {
        "username": username,
        "password": password,
        "host": host,
        "templates": [
            {
                "name": "public",
                "bandwidth": 20
            },
            {
                "name": "private",
                "bandwidth": 100
            }
        ]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "create limit template result: %s" % result


def delete_limit_template(req):
    path = '/baremetal/switch/limit/delete'
    body = {
        "username": username,
        "password": password,
        "host": host,
        "templates": ["public", "private"]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "delete limit template result: %s" % result

def close_port(req):
    path = "/baremetal/port/close"
    body = {
        "username": username,
        "password": password,
        "host": host,
        "ports": ["10GE1/0/11", "10GE1/0/12", "Eth-Trunk 5"]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "close port result: %s" % result


def open_port(req):
    path = "/baremetal/port/open"
    body = {
        "username": username,
        "password": password,
        "host": host,
        "ports": ["10GE1/0/11", "10GE1/0/12", "Eth-Trunk 5"]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "open port result: %s" % result


def init_all_config(req):
    path = "/baremetal/switch/init"
    body = {
        "is_dhclient": True,
        "template_name": "12345678-1000",
        "switches": [
            {
                "username": username,
                "password": password,
                "host": host,
                "vlan_ids": ["1000", "1001", "2000-2005"],
                "ports": ["10GE1/0/11", "10GE1/0/12", "10GE1/0/13"]
            },
            {
                "username": username,
                "password": password,
                "host": host,
                "vlan_ids": ["1000", "1001"],
                "ports": ["10GE1/0/11", "10GE1/0/12", "10GE1/0/13"]
            }
        ]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "init all config result: %s" % result


def clean_all_config(req):
    path = "/baremetal/switch/clean"
    body = {
        "template_name": "12345678-1000",
        "switches": [
            {
                "username": username,
                "password": password,
                "host": host,
                "ports": ["10GE1/0/11", "10GE1/0/12", "10GE1/0/13"]
            },
            {
                "username": username,
                "password": password,
                "host": host,
                "ports": ["10GE1/0/11", "10GE1/0/12", "10GE1/0/13"]
            }
        ]
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "clean all config result: %s" % result

def get_relation_mac_and_port(req):
    path = "/baremetal/switch/relationship"
    body = {
        "username": username,
        "password": password,
        "host": host,
        "vlan": 2000,
        "mac": "6c:92:bf:62:c7:d6"
    }
    data = simplejson.dumps(body)
    (status, result) = req.post(path, data, None)
    print "get relationship result: %s" % result

if __name__ == "__main__":
    rest = RestRequest()

    # set_limit(rest)
    # unset_limit(rest)

    # create_limit_template(rest)
    # delete_limit_template(rest)

    # set_vlan(rest)
    # unset_vlan(rest)

    # init_all_config(rest)
    # clean_all_config(rest)

    # open_port(rest)
    # close_port(rest)

    # get_relation_mac_and_port(rest)

