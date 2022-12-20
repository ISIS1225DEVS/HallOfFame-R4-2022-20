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
import time


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de libros

def init():
    analyzer = model.newAnalyzer()
    return analyzer

# Funciones para la carga de datos

def loadData(analyzer):
    loadstops(analyzer)
    loadrutas(analyzer)
    model.addVertices(analyzer)
    model.addEdges(analyzer)
    model.addTransbordos(analyzer)
    return analyzer

def loadstops(analyzer):
    servicesfile = cf.data_dir + "Challenge-4/Barcelona/bus_stops_bcn-utf8-large.csv"
    input_file = csv.DictReader(open(servicesfile, encoding="utf-8"),
                                delimiter=",")
    for stop in input_file:
        model.addStops(analyzer, stop)
    return analyzer

def loadrutas(analyzer):
    servicesfile = cf.data_dir + "Challenge-4/Barcelona/bus_edges_bcn-utf8-large.csv"
    input_file = csv.DictReader(open(servicesfile, encoding="utf-8"),
                                delimiter=",")
    for ruta in input_file:
        model.addRutas(analyzer, ruta)
    return analyzer

# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo

def getCargaDeDatos(analyzer):
    sizeEE = model.getSizeEstacionesExclusivas(analyzer)
    sizeT = model.getSizeTransbordos(analyzer)
    sizeA = model.getSizeArcos(analyzer)
    lonslats = model.getLonAndLatMinMax(analyzer)
    model.grafoCargaDatos(analyzer)
    return sizeEE, sizeT, sizeA, lonslats

#Req 1

def buscarCaminoPosible(analyzer, inicio, destino):
    start_time = getTime()
    a = model.buscarCaminoPosible(analyzer, inicio, destino)
    end_time = getTime()
    delta_time = deltaTime(start_time, end_time)
    print("El tiempo total del requerimiento es de: " + str(delta_time))
    return a

#Req 2

def caminoMenosEstaciones(analyzer, inicio, destino):
    start_time = getTime()
    b = model.caminoMenosEstaciones(analyzer, inicio, destino)
    end_time = getTime()
    delta_time = deltaTime(start_time, end_time)
    print("El tiempo total del requerimiento es de: " + str(delta_time))
    return b

#Req 3

def reconocerComponentesConectados(analyzer):
    start_time = getTime()
    c = model.reconocerComponentesConectados(analyzer)
    end_time = getTime()
    delta_time = deltaTime(start_time, end_time)
    print("El tiempo total del requerimiento es de: " + str(delta_time))
    return c

#Req 4

def estacionesMasCercanas(analyzer, coordenadasIniciales, coordenadasFinales):
    start_time = getTime()
    d = model.recorridoReq4(analyzer, coordenadasIniciales, coordenadasFinales)
    end_time = getTime()
    delta_time = deltaTime(start_time, end_time)
    print("El tiempo total del requerimiento es de: " + str(delta_time))
    return d

#Req 5

def estacionesAlcanzables(analyzer, estacionInicial, cota):
    start_time = getTime()
    e = model.estacionesAlcanzables(analyzer, estacionInicial, cota)
    end_time = getTime()
    delta_time = deltaTime(start_time, end_time)
    print("El tiempo total del requerimiento es de: " + str(delta_time))
    return e

#Req 6

def caminoEstacionVecindario(analyzer,estacionInicial, vecindario):
    start_time = getTime()
    f = model.caminoEstacionVecindario(analyzer,estacionInicial, vecindario)
    end_time = getTime()
    delta_time = deltaTime(start_time, end_time)
    print("El tiempo total del requerimiento es de: " + str(delta_time))
    return f

#Req 7

def recorridoCircular(analyzer, estacionInicial):
    start_time = getTime()
    g = model.rutaCircular(analyzer, estacionInicial)
    end_time = getTime()
    delta_time = deltaTime(start_time, end_time)
    print("El tiempo total del requerimiento es de: " + str(delta_time))
    return g

def getTime():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)


def deltaTime(start, end):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed