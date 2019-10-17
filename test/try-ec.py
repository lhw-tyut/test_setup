import os

path = "/var/run/console"
os.path.exists(path)

mac1 = "6c:92:bf:62:b9:3a"
mac2 = ["6c92-bf62-b93a"]
a =[i for i in  mac1.split(':') ]
print(a)
b = ''
for i in range (0,len(a)):
    if i%2 != 0:
        print(a[i])
        b = ''.join(a[i]+ "-")
        print(b)
    else:
        print(a[i])
        b.join(a[i])

print(b)