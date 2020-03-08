import tenacity
from concurrent.futures import ThreadPoolExecutor


def checkout_gethardinfo(timeout=10):
    @tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_delay(timeout))
    def _checkout():
        res = None
        if res:
            return res
        else:
            print('a')
            raise Exception("%s get dhcp ip failed")

    res = _checkout()


def test_a(i):
    print(i)
    checkout_gethardinfo()


with ThreadPoolExecutor(max_workers=50) as executor:
    for i in range(5):
        executor.submit(test_a, i)
