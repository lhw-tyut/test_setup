import os
import time

ti = time.time() + 1
print(ti)
a = 1
while True:
    if a == 0:
        print("aaaa")
        break
    if time.time() > ti:
        break
    print("via")
