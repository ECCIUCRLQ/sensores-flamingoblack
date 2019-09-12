import socket
import time
import datetime
import RPi.GPIO as GPIO
from ipcqueue import sysvmq as SYSV

GPIO.setmode(GPIO.BCM)
GPIO_PIR = 7
GPIO.setup(GPIO_PIR, GPIO.IN)

buzon = SYSV.Queue(63)

#file = open("datos.txt", "w+")

try:
    while True:
        if GPIO.input(GPIO_PIR):
            now = datetime.datetime.now()
            buzon.put([1, now], msg_type=1)
            #file.write("Intruder detected. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss") + "\n")
            print("Intruder")            
        else:
            now = datetime.datetime.now()
            buzon.put([0, now], msg_type=1)
            #file.write("Intruder not detected. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss") + "\n")
            print("No intruder")
        time.sleep(1)
except KeyboardInterrupt:
    now = datetime.datetime.now()
    #file.write("User exited. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss"))
    #file.close()
    GPIO.cleanup()
