# coding=utf-8
import os
import time
import sys
from ipcqueue import sysvmq as SYSV

my_queue = SYSV.Queue(14)
first_time = False

def obtener_datos():

    try:
        data = my_queue.get_nowait()
        return data
    except:
        print("No hay datos")
        return 0

def transform_into_key(byte_array):

    my_key = str(byte_array[0]) + str(byte_array[1]) + str(byte_array[2]) + str(byte_array[3])
    return my_key

def update_sensor(key, page):

    data = sensor_manager[key]
    if(data[0] == False):
        data[0] = True
        data[1] = 5 # este numero es para prueba
        # data[1] = metodo de MM que devuelve numero pagina
        data[2] = 0
        if(page == 0):
            update_page_table(0, key)
        else:
            update_page_table(1, key)
    else:
        if(data[3] == 5):
            if(data[2] == 500):
                # llamo a metodo para pedir nueva pagina
                # data[1] = actualizo nuevo numero de pagina
                data[2] = 5
                if(page == 0):
                    update_page_table(0, key)
                else:
                    update_page_table(1, key)
            else:
                data[2] += 5
        else:
            if(data[2] == 40000):
                # llamo a metodo para pedir nueva pagina
                # data[1] = actualizo nuevo numero de pagina
                data[2] = 8
                if(page == 0):
                    update_page_table(0, key)
                else:
                    update_page_table(1, key)
            else:
                data[2] += 8


def update_page_table(update_page, this_page):
    
    if(update_page):
        page_file = open("PageTableIndex.csv", "w+")

        for key in sensor_manager.keys():
            data = sensor_manager[key]
            if(data[1] != -1):
                page_file.write(key + "," + str(data[1]) + "\n")
            else:
                page_file.write(key + "\n")

        page_file.close()
    else:
        page_file = open("PageTableIndex.csv", "r+")
        store_buffer = []
        line = page_file.readline()
        
        while line:
            store_buffer.append(line.strip("\n"))
            line = page_file.readline()
        
        page_file.close()
        os.remove("PageTableIndex.csv")

        new_page_file = open("PageTableIndex.csv", "w+")

        for line in store_buffer:
            if(line.find(this_page) != -1):
                data = sensor_manager[this_page]
                new_page_file.write(line + "," + str(data[1]) + "\n")
            else:
                new_page_file.write(line + "\n")

        new_page_file.close()

def check_registered_sensor(sensor):

    my_key = transform_into_key(sensor)

    for key in sensor_manager:
        if my_key == key:
            return
    
    data_size = len(sensor) - 4
    sensor_manager[my_key] = [False, -1, -1, data_size]
    return

def main():

    global first_time

    try:
        while True:
            
            data = obtener_datos()
            
            if(data != 0):
                sensor_id = bytearray([data[0], data[1], data[2], data[3]])
                sensor_key = transform_into_key(sensor_id)
                check_registered_sensor(sensor_id)

                if(first_time == False):
                    first_time = True
                    update_sensor(sensor_key, 1)
                else:
                    update_sensor(sensor_key, 0)

            time.sleep(1)

    except KeyboardInterrupt:
	    print ("\nInterface shutdown.")
    
    '''
    miArreglo = bytearray([4,0,0,1])
    new_key = transform_into_key(miArreglo)
    update_sensor(new_key)
    update_page_table(1)
    time.sleep(5)
    update_page_table(0)
    '''

sensor_manager = {
    # key: [primera vez, página actual, por donde va en la página, tamaño del dato del sensor]
    "1001": [False, -1, -1, 5],
    "1002": [False, -1, -1, 5],
    "2001": [False, -1, -1, 5],
    "2002": [False, -1, -1, 5],
    "3001": [False, -1, -1, 5],
    "3002": [False, -1, -1, 5],
    "4001": [False, -1, -1, 5],
    "4002": [False, -1, -1, 5],
    "5001": [False, -1, -1, 5],
    "5002": [False, -1, -1, 8],
    "6001": [False, -1, -1, 8],
    "6002": [False, -1, -1, 8]
}

main()