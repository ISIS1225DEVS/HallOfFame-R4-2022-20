"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import tracemalloc
import config as cf
import model
import csv
import time
import tracemalloc
import networkx as nx
import graphviz
import matplotlib.pyplot as plt


csv.field_size_limit(2147483647)

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de juegos

def newController():
    """
    Crea una instancia del modelo
    """
    control = {
        'model': None
    }
    control['model'] = model.newCatalog()
    return control


# Funciones para la carga de datos

def loadData(control,archiv, memory = False):
    start_time = getTime()
    if memory:
        tracemalloc.start()
        start_memory = getMemory()

    catalog = control['model']
    loadEstaciones(catalog,archiv)
    loadRutas(catalog,archiv)

    cont_trans=model.addTransbordo(catalog)

    vertices=model.totalStops(catalog)
    arcos=model.totalConnections(catalog)
    
    stop_time = getTime()
    delta_time = deltaTime(stop_time, start_time)

    #nx.draw_networkx(catalog['G'])
    #plt.show()

    if memory:
        stop_memory = getMemory()
        tracemalloc.stop()
        stop_time = getTime()
        delta_memory = deltaMemory(stop_memory, start_memory)
        return vertices, arcos,cont_trans, delta_time, delta_memory

    else:
        return vertices, arcos,cont_trans, delta_time,None

def loadEstaciones(catalog,archiv):
    booksfile = cf.data_dir + 'bus_stops_bcn-utf8-'+archiv
    input_file = csv.DictReader(open(booksfile, encoding='utf-8'))
    for juego in input_file:
        model.addVertice(catalog, juego)
    return catalog['vertices']

def loadRutas(catalog,archiv):
    booksfile = cf.data_dir + 'bus_edges_bcn-utf8-'+archiv
    input_file = csv.DictReader(open(booksfile, encoding='utf-8'))
    for juego in input_file:
        model.addArco(catalog, juego)
    return catalog['arcos']

    

# Funciones de consulta sobre el catálogo

def getReq1(control,ini,dest):
    resp=model.getReq1(control['model'],ini,dest)
    return resp

def getReq2(control,ini,dest):
    resp=model.getReq2(control['model'],ini,dest)
    return resp

def getReq3(control):
    resp=model.getReq3(control['model'])
    return resp

def getReq4(control,lon_ini,lat_ini,lon_dest,lat_dest):
    resp=model.getReq4(control['model'],lon_ini,lat_ini,lon_dest,lat_dest)
    return resp

def getReq5(control,ini,num):
    resp=model.getReq5(control['model'],ini,num)
    return resp

def getReq6(control,ini,barrio):
    resp=model.getReq6(control['model'],ini,barrio)
    return resp

def getReq7(control,ini):
    resp=model.getReq7(control['model'],ini)
    return resp

# Funciones de tiempo

def getTime():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)

def deltaTime(end, start):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed

def getMemory():
    """
    toma una muestra de la memoria alocada en instante de tiempo
    """
    return tracemalloc.take_snapshot()

def deltaMemory(stop_memory, start_memory):
    """
    calcula la diferencia en memoria alocada del programa entre dos
    instantes de tiempo y devuelve el resultado en bytes (ej.: 2100.0 B)
    """
    memory_diff = stop_memory.compare_to(start_memory, "filename")
    delta_memory = 0.0

    # suma de las diferencias en uso de memoria
    for stat in memory_diff:
        delta_memory = delta_memory + stat.size_diff
    # de Byte -> kByte
    delta_memory = delta_memory/1024.0
    return delta_memory
