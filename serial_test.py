import serial
import serial.tools.list_ports as sp

def setSencor():
    connected_ports = []
    for i in sp.comports():
        connected_ports.append(i.device)

    # print("Connected Ports")
    # for i, port in enumerate(connected_ports):
    #     print(str(i + 1) + ": " + str(port))

    # print("\nSelect one port for serial communication from above")
    # while True:
    #     selected = input()
    #     if selected.isdigit():
    #         selected = int(selected)
    #         if selected > 0 and selected <= len(connected_ports):
    #             break
    #         else:
    #             print("please input valid port index")
    #     else:
    #         print("please input integer")
            
    with serial.Serial() as ser:
        ser.port = connected_ports[2]
        ser.baudrate = 9600
        ser.timeout = 10
        ser.write_timeout = 10
        # ser_sett = ser.get_settings()

        # print("Start serial communication with [" + connected_ports[2] + "]")
        # print(ser_sett)
        ser.open()

        while ser.is_open:
            line = ser.readline()
            value = line.decode().strip()
            print(value, end="\n")

setSencor()