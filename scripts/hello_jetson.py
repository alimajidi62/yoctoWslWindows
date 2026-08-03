import platform
import socket
import datetime

print("=" * 40)
print("  Hello from Jetson Nano!")
print("=" * 40)
print(f"  Hostname : {socket.gethostname()}")
print(f"  OS       : {platform.system()} {platform.release()}")
print(f"  Machine  : {platform.machine()}")
print(f"  Python   : {platform.python_version()}")
print(f"  Time     : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 40)
