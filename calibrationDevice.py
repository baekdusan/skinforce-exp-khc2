import tkinter as tk
import tkinter.font
import serial
import serial.tools.list_ports as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import threading

connected_ports = []
forceList = []
measuredWeightList = []
for i in sp.comports():
    connected_ports.append(i.device)

print("Connected Ports")
for i, port in enumerate(connected_ports):
    print(str(i + 1) + ": " + str(port))

def getPortNum():
    print("\nSelect port for serial communication from above")
    while True:
        selected = input()
        if selected.isdigit():   
            selected = int(selected)
            if selected > 0 and selected <= len(connected_ports):
                return selected
            else:
                print("please input valid port index")
        else:
            print("please input integer")


Ser = serial.Serial()
Ser.port = connected_ports[- 1] #getPortNum()
Ser.baudrate = 9600
Ser.timeout = 10
Ser.write_timeout = 10
loadSer_sett = Ser.get_settings()
print(loadSer_sett)
Ser.open()

# Fitting을 위한 지수함수 정의
def exponential_function(x, a, b):
    return a * np.exp(b * x)



while True:
    cmd = input("Input : ")
    if cmd == 'end':
        Ser.write("0".encode())
        break
    else:
        # print(cmd)
        if cmd == 'o':
            Ser.write(cmd.encode())
            read = Ser.readline().decode().strip()
            print(read)
        elif cmd == 'l':
            Ser.write("d".encode())
            for i in range(10):
                Ser.write("s".encode())
                read = Ser.readline().decode().strip().split(",")
                print(read)
                if float(read[1]) > 10:
                    forceList.append(int(read[0]))
                    measuredWeightList.append(float(read[1]))
        elif cmd == "check":
            Ser.write("d".encode())
            while True:
                Ser.write("s".encode())
                read = Ser.readline().decode().strip()
                if read == "E":
                    break
                else:
                    print(read)
        elif cmd == 'c':
            Ser.write(cmd.encode())
            read = Ser.readline().decode().strip()
            print(read)
        else:
            Ser.write(cmd.encode())

print(forceList)
print(measuredWeightList)
y_data = np.array(measuredWeightList)
x_data = np.array(forceList)

# Curve fitting 수행
popt, _ = curve_fit(exponential_function, x_data, y_data, p0=(1, 0.01))
a_fit, b_fit = popt
print("w: ", measuredWeightList)
print("F: ", forceList)
print("Fitted Parameters:")
print("a =", a_fit)
print("b =", b_fit)

# R제곱 값을 계산
residuals = y_data - exponential_function(x_data, a_fit, b_fit)
ss_res = np.sum(residuals**2)
ss_tot = np.sum((y_data - np.mean(y_data))**2)
r_squared = 1 - (ss_res / ss_tot)

# Fitting된 지수함수 식 출력
fitted_equation = f"Fitted Equation: y = {a_fit:.4f} * exp({b_fit:.4f} * x)"
print(fitted_equation)
print("R-squared =", r_squared)
# 데이터와 fitting된 지수함수 그래프 그리기
x_fit = np.linspace(min(x_data), max(x_data), 100)
y_fit = exponential_function(x_fit, a_fit, b_fit)
plt.scatter(x_data, y_data, label='Data')
plt.plot(x_fit, y_fit, 'r', label='Fitted Exponential')
plt.xlabel('Force')
plt.ylabel('Weight')
plt.legend()
plt.show()


