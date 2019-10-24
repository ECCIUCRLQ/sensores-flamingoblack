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
#siguiente_dato = 0


def convert_time(now):
    value = now.strftime.tm_min(now)
    return value

def count_bins(min_meas, max_meas):
    bin_width = (max_meas - min_meas)/bin_count
    bin_maxes = [] 
    bin_counts = []
    for i in range(bin_count):
        bin_max = min_meas + (i + 1)*bin_width
        bin_maxes.append(bin_max)
        bin_counts.append(0)
    print("bin_maxes " + str(bin_maxes) +"\n")
    print("bin_counts " + str(bin_counts) +"\n")
    return bin_counts, bin_maxes

def count_data_per_bin(datos, bin_maxes, bin_counts, min_meas):
    last_bin = 0
    for i in range(bin_count):
        for j in range(len(datos)):
            if(datos[j]>last_bin and datos[j]<bin_maxes[i]):
                bin_counts[i] +=1
            elif (datos[j]>bin_maxes[i]):
                break
    last_bin = bin_maxes[i]
    return bin_counts

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

def grafic_continious_lines_data_time(datos_value, datos_time, nombreSensorParametro):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=datos_time, y=datos_value, name='Linea dato/tiempo',
                         line=dict(color='firebrick', width=4)))
    nombreGraficador = "Graficador del sensor " + nombreSensorParametro 
    fig.update_layout(title= nombreGraficador,
                   xaxis_title='Fecha y hora',
                   yaxis_title='Datos')
    fig.show()

def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

def grafic_bars_single(datos1):
    min_meas = 0
    max_meas = 0
    bin_counts = []
    bin_maxes = []
    datos_time = []
    datos_value = []

    datos_time, datos_value  = separate_values(datos1)
    min_meas = datos_time[0]
    max_meas = datos_time[len(datos_time)-1]
    bin_counts, bin_maxes = count_bins(min_meas, max_meas)
    print("bin_maxes in method " + str(bin_maxes) +"\n")
    print("bin_counts in method " + str(bin_counts) +"\n")
    bin_counts = count_data_per_bin(datos_value, bin_maxes, bin_counts, min_meas)

    ind = np.arange(bin_count)                  # la localizacion en X de las barras
    width = 0.5                                 # el ancho de las barras
    barras = plt.bar(ind, bin_counts, width)    # crea las barras con los conteos de rangos
    plt.xlabel('Rangos')                        # titulo del eje X
    plt.xticks(ind)                             # valores en el eje X
    plt.ylabel('Frecuencias')                   # titulo del eje Y
    plt.title('Histograma')                     # titulo del grafico
    plt.show()                                  # grafica

def grafic_bars_comparative(datos1, datos2):
    min_meas = 0
    max_meas = 0
    bin_count = []
    bin_maxes = []
    datos_time1 = []
    datos_value1 = []
    datos_time2 = []
    datos_value2 = []
    
    datos_time1, datos_value1  = separate_values(datos1)
    datos_value2, datos_time2 = separate_values(datos2)

    if(datos_time1[0]<datos_time2[0]):
        min_meas = datos_time2[0]
    else:
        min_meas = datos_time1[0]

    if(datos_time1[len(datos_time1)-1]<datos_time2[len(datos_time2)-1]):
        max_meas = datos_time2[len(datos_time2)-1]
    else:
        max_meas = datos_time1[len(datos_time1)-1]


    bin_count, bin_maxes = count_bins(min_meas, max_meas)

    bin_count1 = count_data_per_bin(datos_value1, bin_maxes, bin_count, min_meas)
    bin_count2 = count_data_per_bin(datos_value2, bin_maxes, bin_count, min_meas)

    print("bin_count1 " + str(bin_count1) +"\n")
    print("bin_count2 " + str(bin_count2) +"\n")

    x = np.arange(len(bin_maxes))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, bin_count1, width, label='Sensor 1')
    rects2 = ax.bar(x + width/2, bin_count2, width, label='Sensor 2')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Segundos')
    ax.set_title('Grafico comparativo')
    ax.set_xticks(x)
    ax.set_xticklabels(bin_maxes)
    ax.legend()

    autolabel(rects1, ax)
    autolabel(rects2, ax)

    fig.tight_layout()

    plt.show()


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
        
        #------Parte de grafico de linea continua de dato/tiempo---------
        if sys.argv[2] == "5002" or sys.argv[2] == "6001" or sys.argv[2] == "6002":
            datos_value = []
            datos_time = []
            datos_time, datos_value = separate_values(datos1)
            #conversion de datos de tiempo a fecha legible
            for i in range(len(datos_time)):
                tiempo = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(datos_time[i])) 
                datos_time[i] = tiempo
            
            if sys.argv[2] == "5002":
                for i in range(len(datos_value)):
                    valor = round(datos_value[i], 1)
                    datos_value[i] = valor
            print(datos_value)
            grafic_continious_lines_data_time(datos_value, datos_time, sys.argv[2])    
        
        #------Parte de grafico de linea continua de dato/tiempo---------
        

    elif(len(sys.argv)==4):
        buzon.put(sys.argv[2],block=True)
        datos1 = read_data()
        print("Data recieved 1 " + str(datos1) +"\n")
        buzon.put(sys.argv[3],block=True)
        datos2 = read_data()
        print("Data recieved 2 " + str(datos2) +"\n")
        grafic_bars_comparative(datos1, datos2)
    else:
        print("El ingreso de datos debe ser de la siguiente manera: \n")
        print("Nombre del archivo  'graficador.py' \n")
        print("Tipo de grafico. 'Lineas' o 'barras'. \n")
        print("Sensor Id 1 Por ejemplo '2001' \n")
        print("Sensor Id 2 (si es necesario) Por ejemplo '2002' \n")


main()
