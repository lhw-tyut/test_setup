import httplib
import uuid
from concurrent.futures import ThreadPoolExecutor
import simplejson


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


def pxe_config(req, host):
    path = "/v2/baremetal/ipmi/nic_pxe"
    body = {
        "ip": host["ip"],
        "username": host["username"],
        "password": host["password"],
        "pxe_device": "1,2,3"
    }
    data = simplejson.dumps(body)
    # (status, result) = req.post(path, data, None)

    print body

if __name__ == "__main__":
    rest = RestRequest()

    ipmi_info = [{"ip": "10.128.125.22", "username": "root", "password": "calvin"},
                 {"ip": "10.128.125.23", "username": "root", "password": "calvin"},
                 {"ip": "10.128.125.24", "username": "root", "password": "cds-china"},
                 {"ip": "10.128.125.25", "username": "root", "password": "P@$$w0rd"},
                 ]
    with ThreadPoolExecutor(max_workers=100) as executor:
        for host in ipmi_info:
            executor.submit(pxe_config, rest, host)


