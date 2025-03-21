import serial
import serial.tools.list_ports

print("Start")
# https://pythonhosted.org/pyserial/tools.html#serial.tools.list_ports.ListPortInfo

ports = serial.tools.list_ports.comports()

print(ports)

for port, desc, hwid in sorted(ports):
    print("{}: {} [{}]".format(port, desc, hwid))

# ser = serial.Serial("COM11", 9600)
# if ser.is_open:
#     print(f"{ser} is open")
#     while True:
#         print(ser.readline())


print("Finish")
