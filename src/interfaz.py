# coding=utf-8
import os
import time
import sys
import random
import threading
from ipcqueue import sysvmq as SYSV

colector_queue = SYSV.Queue(14)  # cola para recolector
plotter_queue = SYSV.Queue(15)   # cola para graficador
first_time = False
lock = threading.Lock()

'''
class threadPlotter(threading.Thread):
    def run(self):
        while True:
            plotter_sensor_id = check_plotter_request()
            
            if(plotter_sensor_id != 0):
                all_sensor_data = recover_data_from_memory(plotter_sensor_id)
                plotter_queue.put(all_sensor_data, msg_type = 2)
            else:
                lock.acquire()
                print ("No hay pedidos del graficador.\n")
                lock.release()
                time.sleep(4)
'''

class threadsInterface(threading.Thread):
    
    def run(self):

        my_name = self.getName()
        global first_time

        while True:

            if(my_name == "inter"):
                data = obtain_data_from_recolector()

                if(data != 0):

                    sensor_id = bytearray([data[0], data[1], data[2], data[3]])
                    sensor_key = transform_into_key(sensor_id)
                    check_registered_sensor(sensor_id)

                    if(first_time == False):

                        first_time = True
                        lock.acquire()
                        update_sensor_metadata(sensor_key, 1)
                        lock.release()
                        save_data(sensor_key)

                    else:

                        lock.acquire()
                        update_sensor_metadata(sensor_key, 0)
                        lock.release()
                        save_data(sensor_key)

                    lock.acquire()
                    print ("Obtuve datos (" + my_name + ")\n")
                    lock.release()

                else:

                    lock.acquire()
                    print ("No hay datos (" + my_name + ")\n")
                    lock.release()
                
                time.sleep(4)

            else:
                plotter_sensor_id = check_plotter_request()
            
                if(plotter_sensor_id != 0):

                    lock.acquire()
                    all_sensor_data = recover_data_from_memory(plotter_sensor_id)
                    lock.release()
                    plotter_queue.put(all_sensor_data, msg_type = 2)

                else:

                    lock.acquire()
                    print ("No hay pedidos del graficador (" + my_name + ")\n")
                    lock.release()
                
                time.sleep(4)

def check_plotter_request():

    try:
        sensor_id = plotter_queue.get_nowait()
        return sensor_id
    except:
        return 0

def obtain_data_from_recolector():

    try:
        data = colector_queue.get_nowait()
        return data
    except:
        return 0

def recover_data_from_memory(sensor_id):

    page_file = open("PageTableIndex.csv", "r+")
    line = page_file.readline()
    
    while line:

        if(line.find(sensor_id) != -1):
            line.strip("\n")
            pages_string = line.split(",")
            pages_string.pop(0)
            num_pages = map(int, pages_string)
            print (num_pages)
            #request = llamar a método que devuelve páginas a partir de un array de páginas, en este caso pages
            return num_pages

        line = page_file.readline()
    
    page_file.close()

def transform_into_key(byte_array):

    my_key = str(byte_array[0]) + str(byte_array[1]) + str(byte_array[2]) + str(byte_array[3])
    return my_key

def update_sensor_metadata(key, page):

    data = sensor_manager[key]

    if(data[0] == False):
        data[0] = True
        # llamo a metodo para pedir nueva pagina
        # data[1] = actualizo nuevo numero de pagina
        data[1] = random.randint(0,50)
        data[2] = 0
        if(page == 0):
            update_page_table(0, key)
        else:
            update_page_table(1, key)
    else:
        if(data[3] == 5):
            if(data[2] == 5):
                # llamo a metodo para pedir nueva pagina
                # data[1] = actualizo nuevo numero de pagina
                data[1] = random.randint(0,50)
                data[2] = 0
                if(page == 0):
                    update_page_table(0, key)
                else:
                    update_page_table(1, key)
        else:
            if(data[2] == 40000):
                # llamo a metodo para pedir nueva pagina
                # data[1] = actualizo nuevo numero de pagina
                data[2] = 0
                if(page == 0):
                    update_page_table(0, key)
                else:
                    update_page_table(1, key)

def save_data(key):

    data = sensor_manager[key]

    # llamo a metodo para guardar data en MM con parámetros (# página, offset)
    data[2] += data[3]

def update_page_table(update_page, this_page):
    
    if(update_page):

        if(os.path.isfile("PageTableIndex.csv")):
            print ("remuevo")
            os.remove("PageTableIndex.csv")

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

    threadinter = threadsInterface(name = "inter")
    threadplot = threadsInterface(name = "plot")

    threadinter.start()
    threadplot.start()

    '''
    while True:
        
        data = obtain_data_from_recolector()
        plotter_sensor_id = check_plotter_request()
        
        if(plotter_sensor_id != 0):
            all_sensor_data = recover_data_from_memory(plotter_sensor_id)
            plotter_queue.put(all_sensor_data)

        if(data != 0):
            sensor_id = bytearray([data[0], data[1], data[2], data[3]])
            sensor_key = transform_into_key(sensor_id)
            check_registered_sensor(sensor_id)

            if(first_time == False):
                first_time = True
                update_sensor_metadata(sensor_key, 1)
                save_data(sensor_key)
            else:
                update_sensor_metadata(sensor_key, 0)
                save_data(sensor_key)

        time.sleep(1)
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