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
            now = datetime.datetime.now()
            buzon.put([1, now], msg_type=2)
            #file.write("Light no detected. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss") + "\n")
            print("Obscuridad :(" + str(valor))         
        else:
            now = datetime.datetime.now()
            buzon.put([0, now], msg_type=2)
            #file.write("Light detected. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss") + "\n")
            print("Luz :)" + str(valor))
        time.sleep(1)
except KeyboardInterrupt:
    now = datetime.datetime.now()
    #file.write("User exited. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss"))
    #file.close()
    GPIO.cleanup()
