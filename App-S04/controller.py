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
import os


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""
def newAnalyzer():
    return model.newAnalyzer()

def loadstops(filename):

    analyzer = model.newAnalyzer()
    stopsfile = os.path.join(cf.data_dir, filename)
    catalog = model.addStop(analyzer, stopsfile)
    return catalog


def loadRoute(filename):

    analyzer = model.newAnalyzer()
    routesfile = os.path.join(cf.data_dir, filename)
    catalog = model.addRoute(analyzer, routesfile)
    return catalog

def loadData(filename):
    """
    Carga los datos de los archivos y cargar los datos en la
    estructura de datos
    """
    analyzer = model.newAnalyzer()
    stops = loadstops(filename)
    routes = loadRoute( filename)


    return stops, routes


def addStopsBig(catalog):
    return model.addStopsBig(catalog)

def calculateweight(catalog):
    return model.calculaterouteweight(catalog)

def addEdges(catalog):
    return model.addEdges(catalog)

def addEdgesTransbordos(catalog):
    return model.addEdgesTransbordo(catalog)

def pathStationsDFS(catalog, initialStation, finalStation):
    return model.pathStationsDFS(catalog, initialStation, finalStation)

def pathStationsBFS(catalog, initialStation, finalStation):
    return model.pathStationsBFS(catalog, initialStation, finalStation)

def connectedcomponents(catalog):
    return model.connectedComponenets(catalog)

def connectedcompon(catalog):
    return model.connectedCompon(catalog)

def circularPaths(catalog, station):
    return model.circularpath(catalog, station)

def path_Stations_number(catalog, Station, number):
    return model.path_Station_number(catalog, Station, number)

def shortestPath(catalog, originlong, originlat, destlong, destlat):
    return model.shortestPath(catalog, originlong, originlat, destlong, destlat)

def shortestNeighborhood(catalog, estacionorigen, vecindario):
    return model.shortestNeighborhood(catalog, estacionorigen, vecindario)

# Inicialización del Catálogo de libros

# Funciones para la carga de datos

# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo
