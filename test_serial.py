import serial
import serial.tools.list_ports
import sys

print("Start")
# https://pythonhosted.org/pyserial/tools.html#serial.tools.list_ports.ListPortInfo

ports = serial.tools.list_ports.comports()

print(ports)

for port, desc, hwid in sorted(ports):
    print("{}: {} [{}]".format(port, desc, hwid))


# show ports

# connect selected port


ser = serial.Serial("COM3", 9600)
if ser.is_open:
    print(f"{ser} is open")
    print(ser.readline())

    # read b'Enter number of pins (2-8): \r\n'

    # send n of pins

    ser.write(b"8\n")

    while True:
        # print(ser.readline())
        read_line = ser.readline()
        if read_line:
            print(read_line)

            # b'Typed 8\r\n'
            # b'Transformed to 8\r\n'

            if read_line.startswith(b"Pin N"):

                # read in loop / write something on each read - from table

                # b'Pin N: 4\r\n'
                rl_utf8 = read_line.decode("utf-8")
                print(f"-1 {rl_utf8[-1]}")
                print(f"-2 {rl_utf8[-2]}")
                print(f"-3 {rl_utf8[-3]}")
                ret_str = bytes("привет мир\n", "ascii")
                # cp855 / cp866 / cp1251 / iso8859_5 / utf-8
                print("len", len(ret_str))
                print("sys.getsizeof", sys.getsizeof(ret_str))
                ser.write(ret_str)  # not more 16 bytes
                # break


print("Finish")
