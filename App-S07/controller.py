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
def newController():
    """
    Crea una instancia del modelo
    """
    control = model.newAnalyzer('ARRAY_LIST')
    return control

# Funciones para la carga de datos
def loadData(analyzer, sizeFile):
    contentFile = cf.data_dir + 'Barcelona//bus_stops_bcn-utf8-' + str(sizeFile) + '.csv'
    inputFile = csv.DictReader(open(contentFile, encoding="utf-8"), delimiter=",")
    for busStop in inputFile:
        model.addBusStop(analyzer, busStop)
    contentFile = cf.data_dir + 'Barcelona//bus_edges_bcn-utf8-' + str(sizeFile) + '.csv'
    inputFile = csv.DictReader(open(contentFile, encoding="utf-8"), delimiter=",")
    for busEdge in inputFile:
        model.addBusEdge(analyzer, busEdge)
    analyzer['generalInformation']['busStops'] = model.lt.size(analyzer['busStops'])
    analyzer['generalInformation']['busEdges'] = model.lt.size(analyzer['busEdges'])
    model.connectSharedStops(analyzer)
    return

# Funciones de ordenamiento
def firstAndLastThreeData(lista):
    return model.firstAndLastThreeData(lista)

def firstAndLastFiveData(analyzer, lista, directed):
    return model.firstAndLastFiveData(analyzer, lista, directed)

# Funciones de consulta sobre el catálogo
def findPathBetweenTwoStations(analyzer, stationA, stationB):
    stationA = stationA.upper()
    stationB = stationB.upper()
    return model.findPathBetweenTwoStations(analyzer, stationA, stationB)

def findShortestPath(analyzer, stationA, stationB):
    stationA = stationA.upper()
    stationB = stationB.upper()
    return model.findShortestPath(analyzer, stationA, stationB)

def identifyConnectedComponents(analyzer):
    return model.identifyConnectedComponents(analyzer)

def findShortestPathBetweenGeographicPoints(analyzer, geolocationA, geolocationB):
    return model.findShortestPathBetweenGeographicPoints(analyzer, geolocationA, geolocationB)

def locateReachableStations(analyzer, station, numConnections):
    station = station.upper()
    return model.locateReachableStations(analyzer, station, numConnections)

def findShortestPathBetweenStationAndNeighborhood(analyzer, station, neighborhood):
    station = station.upper()
    neighborhood = neighborhood.title()
    return model.findShortestPathBetweenStationAndNeighborhood(analyzer, station, neighborhood)

def findCircularPath(analyzer, initialStation):
    initialStation = initialStation.upper()
    return model.findCircularPath(analyzer, initialStation)

# Funciones para medir tiempos de ejecucion
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
