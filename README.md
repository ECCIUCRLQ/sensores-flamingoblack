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

### Fase 3: Memoria distribuida

El objetivo de esta etapa es construir una memoria distribuida para el sistema de recolección de datos de sensores del proyecto. La figura 1 muestra los componentes de la red, la topología y los protocolos usados.
A continuación se describen los requerimientos de esta etapa.


![imagen](https://user-images.githubusercontent.com/49280127/68361318-02a57800-00e9-11ea-8cd5-6f8dc0a55831.jpg)

1)	Swapping


Deberán implementarse dos administradores de memoria: uno local y otro distribuido. El administrador local puede ser el mismo utilizado en la etapa 2 del proyecto.

Administrador local: La única restricción es que solo tendrá espacio para cuatro páginas a la vez. Se supondrá que no más de dos sensores al mismo tiempo estarán solicitando a la interfaz local acceso a memoria para almacenar sus datos.

Administrador distribuido: Una vez que una página esté llena, la misma deberá almacenarse en alguno de los nodos disponibles. Para ello deberá discutirse en clase cuál será el criterio apropiado para escoger el nodo donde se desean almacenar las páginas.
Cada nodo de memoria tiene una cantidad máxima parametrizable de memoria disponible para usar en el sistema.

Además, este administrador deberá contar con un servicio de localización de páginas por demanda (interfaz distribuida de memoria). Es decir, la interfaz podrá solicitar al administrador distribuido una serie de páginas; este administrador deberá ser capaz de
 
localizar físicamente la o las páginas solicitadas, recuperarlas y enviarlas a la interfaz. La forma en la que se guardarán las páginas en los nodos será descrita en el siguiente punto.

Con el objetivo de mantener el servicio siempre listo para atender solicitudes, se contará con dos servicios de localización de páginas: uno activo y otro pasivo. El servicio activo será el que responderá las solicitudes de la interfaz. El servicio pasivo estará disponible para que en caso de que el servicio activo deje de funcionar, el servicio pasivo tomará su lugar y comenzará a responder solicitudes. En cualquier momento un servicio pasivo podrá registrarse para que sirva como soporte en caso de que el activo deje de funcionar.

2)	Sistema de archivos

En cada nodo de datos se contará con un archivo binario (de tamaño a discutir) que simulará ser una unidad de disco. En esta unidad de disco deberá implementarse un sistema de archivos que permita hacer lo siguiente:
1.	Identificar las páginas de forma única
2.	Registrar la fecha (hora y día) de creación de cada página
3.	Registrar la fecha (hora y día) del último acceso a cada página
4.	Registrar el tamaño de cada página
5.	Almacenar la ubicación física (en la unidad de disco) de cada página
6.	Listar la información almacenada en la unidad de forma detallada (listar los puntos del 1 al 5 similar a como lo hace el comando ls en Linux). Este servicio bastará con ejecutarse de forma local en el nodo de datos.

Para implementar este sistema de archivos podrá basarse en cualquier sistema existente, y adaptarlo a las necesidades. De alguna forma, cada equipo deberá organizar las páginas dentro de la unidad. Cualquier estructura de datos, registros, etc. que se necesiten, deberán implementarse localmente en los nodos respectivos.

A continuación se describen tres protocolos que son necesarios para que los datos puedan ser transmitidos desde los nodos recolectores hasta los nodos de memoria para que sean almacenados. Un requerimiento importante de red es que los nodos que recolectan datos y los nodos de memoria deben estar en redes distintas para mayor seguridad.

3)	Protocolo Memoria Local – Interfaz de memoria Distribuida (ML-ID) 

Este protocolo debe permitir que:
1.	La memoria local solicite la asignación de una nueva página de memoria.
2.	La memoria local solicite que se guarde una página. Otros requisitos:
3.	La memoria local se comunica únicamente con una dirección IP conocida.

4)	Protocolo Interfaz distribuida – Interfaz distribuida (ID-ID)
 
Este protocolo debe permitir que:
1.	La primera interfaz en el sistema se apodere del rol activo en una dirección IP conocida.
2.	Una interfaz sea elegida como activa cuando varias lo soliciten al mismo tiempo.
3.	Una interfaz pasiva asuma el rol activo cuando la activa no dé señal de vida por más de 10 segundos.

5)	Protocolo Interfaz distribuida - Nodo de memoria (ID-NM) Este protocolo debe permitir que:

1.	Un nodo de memoria comunique que quiere participar como almacenador de datos.
2.	La interfaz distribuida almacene una página de memoria en un nodo.
3.	La interfaz de memoria recupere una página de memoria en un nodo.


Se deberá presentar una demo de esta fase el martes 22 de octubre en horas de clase.

![DGE2](https://user-images.githubusercontent.com/54404955/66105390-9af38e80-e578-11e9-8281-c7f6aaa71614.png)

