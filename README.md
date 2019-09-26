# CI0123 Proyecto Integrador de Redes - Oper
# Grupo 02, II Semestre de 2019

## Integrantes

* Polina 
* Paola
* Marco
* Filip

Este proyecto consiste en construir un sistema operativo capaz de almacenar de forma distribuida información recopilada por sensores. Además, va a constar de cuatro fases, las cuales tendrán objetivos y metas específicas.
## Nombre del equipo 
FlamingoBlack

## Fase actual

### Fase 2: Administración de memoria

Usando como base el código de la etapa anterior, en esta parte del proyecto se desea simular elproceso de administración de memoria y graficar los datos almacenados en dicha memoria. Para ello, considere lo siguiente:
 1. Recuerde que en el enunciado del proyecto se hace referenciaen la etapa 2a un “Recolector”, un “Paginador” y un “Graficador”. En el proceso de diseño de la solución otros componentes podrían necesitarse, por lo que cada equipo tiene libertad para incorporar cuantos componentes sean necesarios.
 2. Actualmente (etapa 1), se reciben los paquetes y todos son procesadospor un mismo proceso. En esta nueva etapa se espera que los mensajes asociados a un sensor sean procesados por un proceso exclusivo para ese sensor. Es decir, si se tienen 5 sensores enviando datos, se tendrán 5 procesos procesando los datos de cada sensor. 
 3. Es permitido tener una lista del total de sensores disponibles con susmetadatos respectivos, de tal modo que se puedan tomar decisiones al almacenarlos datos. Los metadatos por almacenar deberán ser los mismos para cada equipo. 
 4. Cada uno de los procesos recolectores (punto 2) deberá solicitarle a un procesoque actúa como interfaz con el administrador de memoria que reserve memoria (sin tener que especificar un tamaño fijo), para que pueda ser usada para almacenar los datos que lleguen de los sensores. 
 5. Cada proceso que recibe datos de sensores deberá solicitar memoriaa la interfaz una única vez. Al hacerlo, deberá indicarle el tamaño de los datos que serán almacenados cada vez. Por ejemplo, si el paquete del sensor 1 consta de 10 bytes de datos, entonces su interfaz deberá hacer un único llamado malloc-maravilloso (sensorID, 10).
 6. La estrategia de asignación de memoria, es decir, cuántas páginas se asignarán a la vez por sensor, de qué tamaño o tamaños pueden ser las páginas, etc., deberá ser definida por cada equipo y será implementada por la interfaz. 
 7. El graficador debe poder solicitar todos los datos de un sensor específico y generar un gráfico con dicha información. Para efectos prácticos, el graficador no conoce ni necesita conocer la estrategia de asignación de memoria implementada. 
 8. El administrador de memoria solo puede comunicarse con su interfaz. Es decir, el administrador de memoria se encarga de almacenar y recuperar datosa solicitud dela interfaz únicamente. 

Se deberá presentar una demo de esta fase el martes 22 de octubre en horas de clase.

![Diagrama General](https://user-images.githubusercontent.com/54404955/64930681-6483e880-d7f0-11e9-9b1c-997c16740bce.png)

