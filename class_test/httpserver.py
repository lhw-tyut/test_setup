import requests


class RestRequest(object):
    def __init__(self, url):
        self.url = url
        self.headers = self._build_header()

    def _build_header(self):
        headers = {"Content-Type": "application/json",
                   "Connection": "close",
                   "Accept": "application/json"}
        return headers

    def send_request(self, method, token=None, site_id=None, body=None,):

        with requests.Session() as session:
            if method == 'GET':
                req = session.get(self.url, params=body, headers=self.headers)
            else:
                req = session.post(self.url, headers=self.headers)
            status = req.status_code
            if status != 200:
                raise
            result = req.json()

        return status, result

