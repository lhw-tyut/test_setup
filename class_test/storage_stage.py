import requests
import json
import tenacity
from concurrent.futures import ThreadPoolExecutor

HOST_IP = "http://storage-service.gic.pre"
CUSTOMERID = "Triumph"
INTERNALCUSTOMERID = "K8s"
INTERNALUSERID = "K8s"
USERID = "Triumph"
SITEID = "a3c21f88-f356-11ea-800c-f0d4e2e923e0"
GOODSID = 102
NAME = "Triumph"
INSTANCEID = "ff87e6a4-a94d-4521-ad32-4db64ca4f1cd"    # 挂载主机ID
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
        self.customerId = CUSTOMERID
        self.userId = USERID
        self.num = num
        self.siteId = SITEID
        self.goodsId = GOODSID
        self.name = NAME
        self.instanceId = INSTANCEID
        self.internalCustomerId = INTERNALCUSTOMERID
        self.internalUserId = INTERNALUSERID

    def create_disk(self):
        url = HOST_IP + "/bmsdisk/v1/disk/create"
        body = {
            "siteId": self.siteId,
            "name": self.name,
            "size": self.size,
            "num": self.num,
            "customer_id": self.customerId,
            "user_id": self.userId,
            "goodsId": self.goodsId,
            "internalCustomerId": self.internalCustomerId,
            "internalUserId": self.internalUserId
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
            "customer_id": self.customerId,
            "user_id": self.userId,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def detach_disk(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/detach"
        body = {
            "diskId": diskId,
            "customer_id": self.customerId,
            "user_id": self.userId,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def delete_disk(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/delete"
        body = {
            "diskId": diskId,
            "customer_id": self.customerId,
            "user_id": self.userId,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def set_bw(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/bw"
        body = {
            "diskId": diskId,
            "bw": self.bw,
            "customer_id": self.customerId,
            "user_id": self.userId
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def set_iops(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/iops"
        body = {
            "diskId": diskId,
            "customer_id": self.customerId,
            "user_id": self.userId,
            "iops": self.iops,
        }
        rest = RestRequest(url)
        result = rest.send_request(body=json.dumps(body))
        return result["data"]["taskId"]

    def expand_disk(self, diskId):
        url = HOST_IP + "/bmsdisk/v1/disk/expand"
        body = {
            "diskId": diskId,
            "size": 20,
            "customer_id": self.customerId,
            "user_id": self.userId,
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


def multi_task(tasks, func, key):
    futures = []
    status = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for task in tasks:
            future = executor.submit(func, task[key])
            futures.append(future)

        for i in futures:
            status.append(i.result())
    return status


def multi_query_task(tasks, func):
    futures = []
    status = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for task in tasks:
            future = executor.submit(func, task)
            futures.append(future)

        for i in futures:
            status.append(i.result())
    return status


def operate_disk(storage, create_tasks):
    create_disk_finish = multi_task(create_tasks, storage.get_task, "taskId")
    print("create disk finish, %s" % create_disk_finish)
    input("创建块设备完成，输入任意键继续")

    attach_tasksId = multi_task(create_tasks, storage.attach_disk, "diskId")
    attach_status = multi_query_task(attach_tasksId, storage.get_task)
    print("attach disk finish, %s" % attach_status)
    input("挂载块设备完成，输入任意键继续")

    # setBw_tasksId = multi_task(create_tasks, storage.set_bw, "diskId")
    # setBw_status = multi_query_task(setBw_tasksId, storage.get_task)
    # print("set bw disk finish, %s" % setBw_status)
    # input("设置带宽完成，输入任意键继续")
    #
    # setIops_tasksId = multi_task(create_tasks, storage.set_iops, "diskId")
    # setIops_status= multi_query_task(setIops_tasksId, storage.get_task)
    # print("set iops disk finish, %s" % setIops_status)
    # input("设置IOPS完成，输入任意键继续")

    expand_tasksId = multi_task(create_tasks, storage.expand_disk, "diskId")
    expand_status = multi_query_task(expand_tasksId, storage.get_task)
    print("expand disk finish, %s" % expand_status)
    input("扩展磁盘完成，输入任意键继续")

    detach_tasksId = multi_task(create_tasks, storage.detach_disk, "diskId")
    detach_status = multi_query_task(detach_tasksId, storage.get_task)
    print("set detach disk finish, %s" % detach_status)
    input("卸载块设备完成，输入任意键继续")

    delete_tasksId = multi_task(create_tasks, storage.delete_disk, "diskId")
    delete_status = multi_query_task(delete_tasksId, storage.get_task)
    print("delete disk finish, %s" % delete_status)

    input("流程完成")


def test_storage(num):
    storage = StorageAPITest(num)
    # create
    create_tasks = storage.create_disk()
    print("create disks %s" % create_tasks)
    operate_disk(storage, create_tasks)


test_storage(1)



