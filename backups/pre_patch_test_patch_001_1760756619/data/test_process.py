
import time, os
pid_file = "/opt/tps19/data/test_process.pid"
with open(pid_file, "w") as f:
    f.write(str(os.getpid()))

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    os.remove(pid_file)
