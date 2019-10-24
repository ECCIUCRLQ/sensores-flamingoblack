import time
import datetime
import select
import sys
import os
from ipcqueue import sysvmq as SYSV
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

buzon = SYSV.Queue(15)

datos1 = []
datos2 = []
bin_count = 5
siguiente_dato = 0


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
        for j in range(len(datos)):
            if(datos[j]>last_bin and datos[j]<bin_maxes[i]):
                bin_counts[i] +=1
            elif (datos[j]>bin_maxes[i]):
                break
    last_bin = bin_maxes[i]

def grafic_continious_lines_data_time(datos_value, datos_time, nombreSensorParametro):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=datos_time, y=datos_value, name='Linea dato/tiempo',
                         line=dict(color='firebrick', width=4)))
    nombreGraficador = "Graficador del sensor " + nombreSensorParametro 
    fig.update_layout(title= nombreGraficador,
                   xaxis_title='Fecha y hora',
                   yaxis_title='Datos')
    fig.show()


def separate_values(values_mixed):
    value_time = []
    value_data = []
    t_value = 0
    d_value = 1
    while(d_value<len(values_mixed)):
        value_time.append(values_mixed[t_value])
        t_value = t_value + 2
        value_data.append(values_mixed[d_value])
        d_value = d_value + 2
    print("Time " + str(value_time) +"\n")
    print("Data " + str(value_data) +"\n")
    return value_time, value_data


def read_data():
    dato = buzon.get(block = True, msg_type=2)
    while True:
        siguiente_dato = buzon.get(block = True, msg_type=2)
        if(siguiente_dato != 1):
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
        
        #------Parte de grafico de linea continua de dato/tiempo---------
        if sys.argv[2] == "5002" or sys.argv[2] == "6001" or sys.argv[2] == "6002":
            datos_value = []
            datos_time = []
            datos_time, datos_value = separate_values(datos1)
            #conversion de datos de tiempo a fecha legible
            for i in range(len(datos_time)):
                tiempo = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(datos_time[i])) 
                datos_time[i] = tiempo
            grafic_continious_lines_data_time(datos_value, datos_time, sys.argv[2])
        
        #------Parte de grafico de linea continua de dato/tiempo---------
        

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
