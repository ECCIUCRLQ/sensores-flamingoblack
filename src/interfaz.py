# coding=utf-8
import os
import time
import sys
import random
import threading
import administradorMem
import struct
from ipcqueue import sysvmq as SYSV


colector_queue = SYSV.Queue(14)                     # cola para recolector
plotter_queue = SYSV.Queue(15)                      # cola para graficador
first_time = False                                  # variable que revisa si es la primera vez que se ejecuto el programa
lock = threading.Lock()                             # lock para los threads
memory_admin = administradorMem.AdministradorMem()  # instancia del administrador de memoria
pipe_name = "my_pipe"                               # pipe designado para enviar datos al graficador

# -----------------
# Metodo run que va a correr los threads
# Usa locks en zonas criticas para prevenir condiciones de carrera
# -----------------

class threadsInterface(threading.Thread):
    
    def run(self):

        my_name = self.getName()
        global first_time

        if(my_name == "inter"):

            while True:

                data = obtain_data_from_recolector()

                if(data != 0):

                    sensor_id = bytearray([data[0], data[1], data[2], data[3]])
                    data_array = ([data[4], data[5]])
                    
                    sensor_key = transform_into_key(sensor_id)
                    check_registered_sensor(sensor_id)

                    lock.acquire()

                    if(first_time == False):

                        first_time = True
                        #lock.acquire()
                        update_sensor_metadata(sensor_key, 1)
                        #lock.release()
                        save_data(sensor_key, data_array)

                    else:

                        #lock.acquire()
                        update_sensor_metadata(sensor_key, 0)
                        #lock.release()
                        save_data(sensor_key, data_array)

                    #lock.acquire()

                    print ("Obtuve datos (" + my_name + ")\n")
                    lock.release()

                else:

                    lock.acquire()
                    print ("No hay datos (" + my_name + ")\n")
                    lock.release()
                
                time.sleep(4)

        else:

            while True:

                plotter_sensor_id = check_plotter_request()
                data = sensor_manager[plotter_sensor_id]
            
                if(plotter_sensor_id != 0):

                    lock.acquire()

                    all_sensor_data = recover_data_from_memory(plotter_sensor_id)
                    plotter_queue.put("Datos se están mandado")
                    send_through_pipe(all_sensor_data)
                    print ("Datos se han mandado al graficador")

                    lock.release()

                else:

                    lock.acquire()
                    print ("No hay pedidos del graficador (" + my_name + ")\n")
                    lock.release()
                
                time.sleep(4)

# -----------------
# Revisa si el graficador ha hecho algun pedido
# -----------------

def check_plotter_request():

    try:
        sensor_id = plotter_queue.get_nowait()
        return sensor_id
    except:
        return 0

# -----------------
# Revisa si el recolector ha mandado datos
# -----------------

def obtain_data_from_recolector():

    try:
        data = colector_queue.get_nowait()
        return data
    except:
        return 0

# -----------------
# Envia todos los datos del sensor que pidio el graficador a traves de un pipe
# -----------------

def send_through_pipe(data):

    if not os.path.exists(pipe_name):

        os.mkfifo(pipe_name)

    pipeout = os.open(pipe_name, os.O_WRONLY)
    os.write(pipeout, str(data))

# -----------------
# Accede a la tabla de paginas en memoria secundaria y obtiene todas las paginas de un sensor
# Luego llama a meotdo del administrador que devuelve todos los datos de las respectivas paginas
# -----------------

def recover_data_from_memory(sensor_id):

    data = sensor_manager[sensor_id]
    page_file = open("PageTableIndex.csv", "r+")
    line = page_file.readline()
    
    while line:

        if(line.find(sensor_id) != -1):
            
            line.strip("\n")
            pages_string = line.split(",")
            pages_string.pop(0)
            
            num_pages = map(int, pages_string)
            all_data = memory_admin.obtenerDatos(data[3], num_pages)
            return all_data

        line = page_file.readline()
    
    page_file.close()

# -----------------
# Transforma el sensor_id en una llave para acceder a la hash
# -----------------

def transform_into_key(byte_array):

    my_key = str(byte_array[0]) + str(byte_array[1]) + str(byte_array[2]) + str(byte_array[3])
    return my_key

# -----------------
# Metodo que actualiza la hash de sensor_manager.
# Actualiza todos los metadatos del sensor de acuerdo a las operaciones que se hayan hecho.
# -----------------

def update_sensor_metadata(key, page):

    data = sensor_manager[key]

    if(data[0] == False):

        # data[1] = random.randint(0,50) dato para prueba

        data[0] = True
        data[1] = memory_admin.reservarPagina(data[3])
        data[2] = 0
        
        if(page == 0):
            update_page_table(0, key)
        else:
            update_page_table(1, key)
    
    else:

        if(data[3] == 5):
            
            if(data[2] == 5):
                
                # data[1] = random.randint(0,50) dato para prueba

                data[1] = memory_admin.reservarPagina(data[3])
                data[2] = 0

                if(page == 0):
                    update_page_table(0, key)
                else:
                    update_page_table(1, key)

        else:

            if(data[2] == 40000):

                # data[1] = random.randint(0,50) dato para prueba

                data[1] = memory_admin.reservarPagina(data[3])
                data[2] = 0

                if(page == 0):
                    update_page_table(0, key)
                else:
                    update_page_table(1, key)

# -----------------
# Metodo que llama al metodo de la clase del administrador de memoria para guardar dato.
# Se va a transformar la fecha y el dato del sensor a un byte array para guardar en memoria.
# -----------------

def save_data(key, data_to_be_saved):

    data = sensor_manager[key]

    sensor_date_bytes = struct.pack("I", data_to_be_saved[0])
    
    if data[3] == 5:
    
        sensor_data_bytes = struct.pack("B", data_to_be_saved[1])
        data_array = bytearray([sensor_date_bytes[0], sensor_date_bytes[1], sensor_date_bytes[2], sensor_date_bytes[3], sensor_data_bytes[0]])

    else:

        sensor_data_bytes = struct.pack("f", data_to_be_saved[1])
        data_array = bytearray([sensor_date_bytes[0], sensor_date_bytes[1], sensor_date_bytes[2], sensor_date_bytes[3], 
                                sensor_data_bytes[0], sensor_data_bytes[1], sensor_data_bytes[2], sensor_data_bytes[3]])

    memory_admin.guardarDato(data[3], data[1], data[2], data_array)
    data[2] += data[3]

# -----------------
# Metodo que actualiza la tabal de paginas que esta en memoria secundaria.
# Este metodo se invoca cada vez que un sensor necesite resrvar una nueva pagina.
# -----------------

def update_page_table(update_page, this_page):
    
    if(update_page):

        if(os.path.isfile("PageTableIndex.csv")):
            print ("Remuevo")
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

# -----------------
# Metodo que revisa si un sensor que mando datos está registrado en la tabla quemada de sensores.
# Si no es asi, lo agrega a la tabla, y establece todos sus respectivos campos.
# -----------------

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

# -----------------
# Hash que mantiene todos los metadatos de los sensores
# -----------------

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