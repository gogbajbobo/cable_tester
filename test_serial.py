import serial.tools.list_ports

print("Start")
# https://pythonhosted.org/pyserial/tools.html#serial.tools.list_ports.ListPortInfo

ports = serial.tools.list_ports.comports()

print(ports)

for port, desc, hwid in sorted(ports):
    print("{}: {} [{}]".format(port, desc, hwid))


print("Finish")
