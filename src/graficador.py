import time
import datetime
import select
import sys
import os
from ipcqueue import sysvmq as SYSV
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

buzon = SYSV.Queue(15)

datos1 = []
datos2 = []
bin_count = 5


def convert_time(now):
    value = now.strftime.tm_min(now)
    return value

def count_bins(min_meas, max_meas, datos):
    bins_width = (max_meas - min_meas)/bin_count
    bin_maxes = [] 
    bin_counts = []
    
    for i in range(bin_count):
        bin_max = min_meas + (i + 1)*bin_width
        bin_maxes.append(bin_max)
        bin_counts.append(0)
    return bin_maxes, bin_counts

def count_data_per_bin(datos, bin_maxes, bin_count, min_meas, ):
    last_bin = 0
    for i in range(bin_count):
        for j in range(datos.length()):
            if(datos[j]>last_bin and datos[j]<bin_maxes[i]):
                bin_counts[i] +=1
            elif (datos[j]>bin_maxes[i]):
                break
    last_bin = bin_maxes[i]

def graphic_bars_two_sensors():



def separate_values(values_mixed):
    value_time = []
    value_data = []
    t_value = 0
    d_value = 1
    while(d_value<values_mixed.length()):
        value_time.apend(values_mixed[t_value])
        t_value = t_value + 2
        value_data.append(values_mixed[d_value])
        d_value = d_value + 2
    return value_time, value_data


def read_data():
    dato = buzon.get(block = True, msg_type=2)
    while True:
        siguiente_dato = buzon.get(block = True, msg_type=2)
        if(Siguiente_dato != 1):
            print("Data recieved " + str(dato) +"\n")
            dato.append(siguiente_dato)
        else:
            break
    return dato


def main():
    if(len(sys.argv)==3):
        buzon.put(sys.argv[2],block=True)
        datos1 = read_data()
        print("Data recieved " + str(datos1) +"\n")
            #print 'Parent %d got "%s" at %s' % (os.getpid(), line, time.time( ))
    elif(len(sys.argv)==4):
        buzon.put(sys.argv[2],block=True)
        read_data()
            
        buzon.put(sys.argv[3],block=True)
        read_data()
    else:
        print("El ingreso de datos debe ser de la siguiente manera: \n")
        print("Nombre del archivo \n")
        print("Tipo de grafico. \n")
        print("Sensor Id 1 \n")
        print("Sensor Id 2 (si es necesario) \n")


main()