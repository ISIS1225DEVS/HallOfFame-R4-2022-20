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


from Clases.Model import Model
from Clases.BusRoute import BusRoute
from Clases.Station import Station
from Clases.Rendimiento import Rendimiento
from DISClib.ADT import list as lt
from datetime import datetime
import config as cf
import model as model

import csv
import time
import tracemalloc
from math import radians, cos, sin, asin, sqrt

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Funciones para medir tiempos de ejecucion

def getTime():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)

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

# Funciones para medir la memoria utilizada

def getMemory():
    """
    toma una muestra de la memoria alocada en instante de tiempo
    """
    return tracemalloc.take_snapshot()



def deltaTime(end, start):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed


def Tiempo_de_carga_loadData(file_size, control, memflag=True):
    """
    Carga los datos de los archivos y cargar los datos en la
    estructura de datos
    """
    # TODO: lab 7, implementacion del catalogo midiendo el tiempo y memoria
    # toma el tiempo al inicio del proceso
    start_time = getTime()

    # inicializa el proceso para medir memoria
    if memflag is True:
        tracemalloc.start()
        start_memory = getMemory()
    print("\nCargando información de los archivos ....\n")    
    loadData(control, file_size)

    # toma el tiempo al final del proceso
    stop_time = getTime()
    # calculando la diferencia en tiempo
    delta_time = deltaTime(stop_time, start_time)

    # finaliza el proceso para medir memoria
    if memflag is True:
        stop_memory = getMemory()
        tracemalloc.stop()
        # calcula la diferencia de memoria
        delta_memory = deltaMemory(stop_memory, start_memory)
        # respuesta con los datos de tiempo y memoria
        return delta_time, delta_memory

    else:
        # respuesta sin medir memoria
        return delta_time

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def newController():
    """
    Crea una instancia del modelo
    """

    control = {'model': None}
    control['model'] = Model()
    return control


#
#   Carga kis archivos
#

def loadData(control, file_size):
    modelClass = control["model"]

    bus_edges_bcn_file = cf.data_dir + 'Barcelona/bus_edges_bcn-utf8-' + file_size +'.csv'
    bus_stops_bcn_file = cf.data_dir + 'Barcelona/bus_stops_bcn-utf8-' + file_size +'.csv'

    print("Cargando STOPS ",bus_stops_bcn_file)
    input_file_1 = csv.DictReader(open(bus_stops_bcn_file, encoding='utf-8'))
    print("Procesando ",bus_stops_bcn_file, end="")
    for line_archive in input_file_1:
        station = Station(line_archive["Code"], float(line_archive["Latitude"]), float(line_archive["Longitude"]), line_archive["District_Name"], line_archive["Neighborhood_Name"], line_archive["Transbordo"])
        bus_route = BusRoute(line_archive["Bus_Stop"])
        model.add_carga_bus_stops(modelClass,line_archive["Code"],station, bus_route,line_archive)
        vertice = line_archive["Code"]+"-"+line_archive["Bus_Stop"].replace("BUS-","")
        modelClass.addGraphVertex(vertice)
        if line_archive["Transbordo"] == "S":
            modelClass.addGraphVertex("T-"+ line_archive["Code"])
            modelClass.addGraphEdge(vertice, "T-"+ line_archive["Code"],0)
            modelClass.addGraphEdge("T-"+ line_archive["Code"],vertice,0)


    input_file_1 = None
    print("\rProcesado ",bus_stops_bcn_file)

    print("Cargando EDGES ",bus_edges_bcn_file)
    input_file_2 = csv.DictReader(open(bus_edges_bcn_file, encoding='utf-8'))
    print("Procesando ",bus_edges_bcn_file,end="")
    for line_archive in input_file_2:
        model.add_carga_bus_edges(modelClass,line_archive)
    print("\rProcesado ",bus_edges_bcn_file)
                
    
#------------------------------------------------------------------------
#===================---------------====================================
#===================requerimientos ==================================== 
#===================---------------====================================


def requerimiento_1(modelClass, origen, destino):
    return model.requerimiento_1(modelClass, origen, destino)

def requerimiento_2(modelClass, origen, destino):
    return model.requerimiento_2(modelClass, origen, destino)

def requerimiento_3(modelClass):
    return model.requerimiento_3(modelClass)

def requerimiento_4(modelClass, lonOrigen, latOrigen, lonDestino, latDestino):
    return model.requerimiento_4(modelClass, lonOrigen, latOrigen, lonDestino, latDestino)

def requerimiento_6(modelClass, vertice_origen, vecindario_destino):
    return model.requerimiento_6(modelClass, vertice_origen, vecindario_destino)

def requerimiento_7(modelClass, vertice_origen):
    return model.requerimiento_7(modelClass, vertice_origen)