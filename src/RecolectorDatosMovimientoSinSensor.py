#import RPi.GPIO as GPIO
import socket
import time
import datetime
import random
from ipcqueue import sysvmq as SYSV

#GPIO.setmode(GPIO.BCM)
#GPIO_PIR = 26
#GPIO.setup(GPIO_PIR, GPIO.IN)

buzon = SYSV.Queue(63)
cambioDeEstado = 1
#file = open("datos.txt", "w+")

try:
    while True:
        valor = random.randint(0, 1)
        #este if es del keep alive
        if cambioDeEstado == valor:
            now = time.time()
            buzon.put([2, 1, now])
            #file.write("Intruder detected. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss") + "\n")
            print("Keep Alive " +  str(time.ctime(now)))
            #print(buzon.get()) 
        else:
            if valor:
                now = time.time()
                buzon.put([1, 1, now])
                #file.write("Intruder detected. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss") + "\n")
                print("Intruder " +  str(time.ctime(now)))
                #print(buzon.get())
                cambioDeEstado = 1             
            else:
                cambioDeEstado = 0 
        time.sleep(1)
except KeyboardInterrupt:
    now = time.time()
    #file.write("User exited. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss"))
    #file.close()
    #GPIO.cleanup()
