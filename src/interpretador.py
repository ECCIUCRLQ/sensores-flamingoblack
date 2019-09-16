
import sys
import struct
import time
import socket
import time
import datetime
import os
from ipcqueue import sysvmq as SYSV

KEY = 36

buzon = SYSV.Queue(KEY)

carpeta_equipo = {
    1:'/Sensores/Whitenoise'
    2:'/Sensores/FlamingoBlack'
    3:'/Sensores/GISSO'
    4:'/Sensores/KOF'
    5:'/Sensores/Equipo404'
    6:'/Sensores/Poffis'
}

archivo_sensor = {
    1:"Movimiento.txt"
    2:"BigSound.txt"
    3:"Fotoresistor.txt"
    4:"Shock.txt"
    5:"Touch.txt"
    6:"Humedad.txt"
    7:"BigSound.txt"
    8:"Tmperatura.txt"
    9:"Ultrasonico.txt"
}

def desempacar(datos):
    fecha = time.ctime(datos[0])
    equipo_sensor = datos[1]
    seq_sensor = datos[2] + datos[3] + datos[4]
    tipo = datos[5]
    evento = datos[6]


try:
    while True:
        data_packed = buzon.get(block=True, msg_type=0)
        data_unpacked = struct.unpack('IBBBBBf', data_packed)
        if not os.path.isdir(carpeta_equipo[data_unpacked[1]]):
            os.makedirs(carpeta_equipo[data_unpacked[1]])
        archivo = open(carpeta_equipo[data_unpacked[5], "a+")
        archivo.write(data_unpacked[0] + data_unpacked[6] + "\n")
        archivo.close()


except KeyboardInterrupt:
    now = datetime.datetime.now()
    file.write("User exited. Date " + now.strftime("%d/%m/%Y Time %Hh:%Mm:%Ss"))
    file.close()
