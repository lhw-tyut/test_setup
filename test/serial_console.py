import os
import subprocess


a = "10.177.178.133"
pid_dir = "/var/run/console"
print(a.split('.')[-1])
test = os.path.join(pid_dir, "host-%s.pid" % a.replace('.', '_'))
print(test)

pidfile = a.replace('.', '_')
print(pidfile)