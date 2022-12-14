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

import config as cf
import model
import csv
import tracemalloc


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización
def initCatalog():
    return model.initCatalog()

# Función para cargar los datos
def loadData(catalog, pct):
    file_bus_edges = f"{cf.data_dir}Barcelona//bus_edges_bcn-utf8-{pct}.csv"
    file_bus_stops = f"{cf.data_dir}Barcelona//bus_stops_bcn-utf8-{pct}.csv"

    dicts_bus_edges = csv.DictReader(open(file_bus_edges, encoding="utf-8"), delimiter=",")
    dicts_bus_stops = csv.DictReader(open(file_bus_stops, encoding="utf-8"), delimiter=",")

    for edge in dicts_bus_edges:
        model.addLtEdges(catalog, edge)
    for stop in dicts_bus_stops:
        model.addLtStops(catalog, stop)

    model.addMapStations(catalog)
    model.addMapNH(catalog)
    model.addStops(catalog)
    model.addEdges(catalog)

    return model.loadData(catalog)

# Funciones de consulta sobre el catálogo
# Req. 1
def routeStations(catalog, station_i, station_f):
    return model.routeStations(catalog, station_i, station_f)

# Req. 2
def fewStops(catalog, station_i, station_f):
    return model.fewStops(catalog, station_i, station_f)

# Req. 3
def connectedComponents(catalog):
    return model.component(catalog)

# Req. 4
def planShortRoute(catalog, lon_i, lat_i, lon_f, lat_f):
    return model.planShortRoute(catalog, lon_i, lat_i, lon_f, lat_f)

# Req. 5
def reachable_stations(catalog: dict, id_org: str, num_max: int):
    return model.reachable_stations(catalog, id_org, num_max)

# Req. 6
def routeStationNH(catalog, station_i, nh):
    return model.routeStationNH(catalog, station_i, nh)

# Req. 7
def circularPath(catalog, station_i):
    return model.circularPath(catalog, station_i)

# Funciones para Tests
def runReqTests(i, catalog):
    """
    Ejecuta las pruebas de los requerimientos y retorna el tiempo que tarda
    """
    tiempo = 0
    # requerimiento 1
    if i == 1:
        init_time = getTime()
        routeStations(catalog, "533-127", "49-H10")
        final_time = getTime()
        tiempo = deltaTime(final_time, init_time)
    # requerimiento 2
    elif i == 2:
        init_time = getTime()
        fewStops(catalog, "12-106", "49-H10")
        final_time = getTime()
        tiempo = deltaTime(final_time, init_time)
    # requerimiento 3
    elif i == 3:
        init_time = getTime()
        #getRecordinRange(catalog, 21, 75)
        final_time = getTime()
        tiempo = None
    # requerimiento 4
    elif i == 4:
        init_time = getTime()
        planShortRoute(catalog, 2.154352, 41.43958, 2.117326, 41.33404)
        final_time = getTime()
        tiempo = deltaTime(final_time, init_time)
    # requerimiento 5
    elif i == 5:
        init_time = getTime()
        #getRecentRecordsInTime(catalog, 542.10, 1887.50)
        final_time = getTime()
        tiempo = None #deltaTime(final_time, init_time)
    # requerimiento 6
    elif i == 6:
        init_time = getTime()
        routeStationNH(catalog, "15-107", "el Poble-sec")
        final_time = getTime()
        tiempo = deltaTime(final_time, init_time)
    # requerimiento 7
    elif i == 7:
        init_time = getTime()
        circularPath(catalog, "34-109")
        final_time = getTime()
        tiempo = deltaTime(final_time, init_time)

    return tiempo

def runMemoryTest(i, catalog):
    tracemalloc.start()
    start_memory = getMemory()

    if i == 1:
        routeStations(catalog, "533-127", "49-H10")
    # requerimiento 2
    elif i == 2:
        fewStops(catalog, "12-106", "49-H10")
    # requerimiento 3
    elif i == 3:
        pass #req 3
    # requerimiento 4
    elif i == 4:
        planShortRoute(catalog, 2.154352, 41.43958, 2.117326, 41.33404)
    # requerimiento 5
    elif i == 5:
        pass#  req 5
    # requerimiento 6
    elif i == 6:
        routeStationNH(catalog, "15-107", "el Poble-sec")
    # requerimiento 7
    elif i == 7:
        circularPath(catalog, "34-109")
    # requerimiento 8


    stop_memory = getMemory()
    tracemalloc.stop()
    # calcula la diferencia de memoria
    delta_memory = deltaMemory(start_memory, stop_memory)
    # respuesta con los datos de memoria
    return delta_memory


def getTime():
    """
    Obtiene el tiempo
    """
    return model.getTime()

def deltaTime(final_time, init_time):
    """
    Obtiene el delta tiempo
    """
    return model.deltaTime(final_time, init_time)

def getMemory():
    """
    toma una muestra de la memoria alocada en instante de tiempo
    """
    return tracemalloc.take_snapshot()

def deltaMemory(start_memory, stop_memory):
    """
    calcula la diferencia en memoria alocada del programa entre dos
    instantes de tiempo y devuelve el resultado en kBytes (ej.: 2100.0 kB)
    """
    memory_diff = stop_memory.compare_to(start_memory, "filename")
    delta_memory = 0.0
    # suma de las diferencias en uso de memoria
    for stat in memory_diff:
        delta_memory = delta_memory + stat.size_diff
    # de Byte -> kByte
    delta_memory = delta_memory/1024.0
    return delta_memory

def connectedComponents(catalog):
    return model.component(catalog)
