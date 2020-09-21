import requests
import json
import tenacity
from concurrent.futures import ThreadPoolExecutor

HOST_IP = "http://storage-service.gic.pre"
retry_kwargs = {
            "reraise": True,
            "wait": tenacity.wait_random(min=3, max=4),
            "stop": tenacity.stop_after_attempt(100)}


class RestRequest(object):

    def __init__(self, url):
        self.url = url
        self.headers = self._build_header()

    def _build_header(self):
        headers = {"Content-Type": "application/json",
                   "Connection": "close",
                   "Accept": "application/json"}
        return headers

    def send_request(self, method="POST", body=None):

        with requests.Session() as session:
            if method == "GET":
                req = session.get(self.url, params=body, headers=self.headers)
            else:
                req = session.post(self.url, data=body, headers=self.headers)
            status = req.status_code
            if status != 200:
                raise
            result = req.json()

        return result


class StorageAPITest(object):
    def __init__(self, num):
        self.size = 10
        self.iops = 10
        self.bw = 10
        self.customerId = "lhw_test"
        self.userId = "lhw_test"
        self.num = num
        self.siteId = "a3c21f88-f356-11ea-800c-f0d4e2e923e0"
        self.goodsId = "647cc0a9-f357-11ea-b3f2-005056abeb9b"
        self.name = "lhw_test"
        self.instanceId = "000484e0-8df1-4b4b-888d-8322900e3c88"

    def create_disk(self):
        url = HOST_IP + "/bmsdisk/v1/disk/create"
        body = {
            "siteId": self.siteId,
            "name": self.name,
            "size": self.size,
            "num": self.num,
            "customerId": self.customerId,
            "userId": self.userId,
            "goodsId": self.goodsId
        }
        rest = RestRequest(url)
        print(url)
        print(body)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["diskInfo"]

    def attach_disk(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/attach"
        body = {
            "instanceId": self.instanceId,
            "diskId": diskId,
            "customerId": self.customerId,
            "userId": self.userId,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def detach_disk(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/detach"
        body = {
            "diskId": diskId,
            "customerId": self.customerId,
            "userId": self.userId,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def delete_disk(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/delete"
        body = {
            "diskId": diskId,
            "customerId": self.customerId,
            "userId": self.userId,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def set_bw(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/bw"
        body = {
            "diskId": diskId,
            "bw": self.bw,
            "customerId": self.customerId,
            "userId": self.userId
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def set_iops(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/iops"
        body = {
            "diskId": diskId,
            "customerId": self.customerId,
            "userId": self.userId,
            "iops": self.iops,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def expand_disk(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/expand"
        body = {
            "diskId": diskId,
            "size": self.size,
            "customerId": self.customerId,
            "userId": self.userId,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    @tenacity.retry(**retry_kwargs)
    def get_task(self, taskId):
        url = HOST_IP + "/bmsdisk/v1/inquire/task/" + taskId
        rest = RestRequest(url)
        result = rest.send_request(method="GET")
        if result["data"]["status"] != "finish":
            raise
        print(result["data"]["status"])
        return result["data"]["status"]


def operate_disk(storage, task):
    storage.get_task(task["taskId"])

    task_id = storage.attach_disk(task["diskId"])
    print("%s attach disk %s" % (task["diskId"], task_id))
    storage.get_task(task_id)

    task_id = storage.set_bw(task["diskId"])
    print("%s bw disk %s" % (task["diskId"], task_id))
    storage.get_task(task_id)

    task_id = storage.set_iops(task["diskId"])
    print("%s iops disk %s" % (task["diskId"], task_id))
    storage.get_task(task_id)

    task_id = storage.expand_disk(task["diskId"])
    print("%s expand disk %s" % (task["diskId"], task_id))
    storage.get_task(task_id)

    task_id = storage.detach_disk(task["diskId"])
    print("%s detach disk %s" % (task["diskId"], task_id))
    storage.get_task(task_id)

    task_id = storage.delete_disk(task["diskId"])
    print("%s delete disk %s" % (task["diskId"], task_id))
    storage.get_task(task_id)


def test_storage(num):
    storage = StorageAPITest(num)
    # create
    create_tasks = storage.create_disk()
    print("create disks %s" % create_tasks)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for task in create_tasks:
            executor.submit(operate_disk, storage, task)


test_storage(1)


