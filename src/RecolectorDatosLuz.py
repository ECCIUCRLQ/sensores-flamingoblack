import RPi.GPIO as GPIO
import socket
import time
import datetime
from ipcqueue import sysvmq as SYSV

GPIO.setmode(GPIO.BCM)
GPIO_PIR = 4
GPIO.setup(GPIO_PIR,GPIO.IN)

buzon = SYSV.Queue(63)
#file = open("datos.txt", "w+")

try:
    while True:
        valor = GPIO.input(GPIO_PIR)
        if valor:
            now = time.time()
            buzon.put([1, 2, now])
            #file.write("Light no detected. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss") + "\n")
            print("Luz :) " + str(time.ctime(now))) 
            #print(buzon.get())       
        else:
            now = time.time()
            buzon.put([2, 2, now])
            #file.write("Intruder detected. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss") + "\n")
            print("Keep Alive " +  str(time.ctime(now)))
            #print(buzon.get()) 
        time.sleep(1)
except KeyboardInterrupt:
    now = time.time()
    #file.write("User exited. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss"))
    #file.close()
    GPIO.cleanup()
