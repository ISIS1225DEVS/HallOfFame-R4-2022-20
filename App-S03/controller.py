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
from DISClib.Algorithms.Sorting import mergesort as merge

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de paradas

def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer


# Funciones para la carga de datos


def loadServices(analyzer, stopsfile, edgesfile):
    lista_max_min = []
    total_estaciones_exclusivas = 0
    total_estaciones_transbordo = 0
    total_rutas_bus = 0
    lat_max = 0;
    lat_min = 100;
    long_max = 0;
    long_min = 100;

    """
    Carga los datos de los archivos CSV en el modelo.
    Se crea un arco entre cada par de estaciones que
    pertenecen al mismo servicio y van en el mismo sentido.

    addRouteConnection crea conexiones entre diferentes rutas
    servidas en una misma estación.
    """
    input_file_stops = csv.DictReader(open(cf.data_dir + stopsfile, encoding="utf-8"),
                                delimiter=",")
    input_file_edges = csv.DictReader(open(cf.data_dir + edgesfile, encoding="utf-8"),
                                delimiter=",")
    
      

    # 1. Creo 2 tablas: una para almacenar la informacion de todos los vertices y otra para almacenar la de los transborods
    # Tabla vertices: llaves son "Code-bus", valores son diccionarios con la info
    # Tabla transbordos: llaves son "Code", valores son los numeros de bus asociados a esa parada
    # 2. Anado a la tabla grande los tipo S y los tipo N
    # 3. Anado a la tabla de transbordos los transbordos, la idea es que como es una tabla de hash, todos los de llave repetida se guarden en la misma llave
    # 4. Anado al grafo las llaves de la tabla grande y quedan de la forma Code-Bus
    # 5. Anado al grafo las llaves de la tabla de transbordos de la forma T-numero
    # 6. Ingreso al archivo de arcos y calculo pesos de cada uno, usando la longitud y la latitud almacenada en la tabla de vertices
    # 7. Uno vertices de transbordo con las estaciones almacenadas en la tabla repetidas

    for stop in input_file_stops:
        bus_stop = stop["Bus_Stop"].split('-')
        bus_stop = bus_stop[1].strip(' ')
        nombre = stop["Code"] + '-' + bus_stop 
        model.tablitaInfo(analyzer,nombre,stop)
        
        if stop["Transbordo"] == "S":
            booleano = model.addTransbordotoTabla(analyzer, stop["Code"], bus_stop)
            if booleano == False:
                total_estaciones_transbordo += 1
        if stop["Transbordo"] == "N":
            total_estaciones_exclusivas += 1
        #creamos el mapa de vecindarios
        model.addVecindarioStation(analyzer, stop)
    
    for edge in input_file_edges:
        bus_name = edge["Bus_Stop"].split('-')
        bus_name = bus_name[1]
        inicio = edge["Code"] + "-" + bus_name
        fin = edge["Code_Destiny"] + "-" + bus_name   
        lat_max_n, lat_min_n, long_max_n, long_min_n, peso = model.calcular_peso(analyzer,inicio, fin, lat_max, lat_min, long_max, long_min )  #editar esta funcion
        lat_max, lat_min, long_max, long_min = lat_max_n, lat_min_n, long_max_n, long_min_n 
        model.crearBosque(analyzer, inicio, fin, peso)

    model.unirTransbordos(analyzer)
    return total_estaciones_exclusivas, total_estaciones_transbordo,lat_max, lat_min, long_max, long_min

    
# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo

#req 1
def existsPath(analyzer,station1,station2):
    return model.existsPath(analyzer, station1, station2)
#req 2
def shortestPath(analyzer,station1, station2):
    return model.shortestPath(analyzer,station1, station2)
#req 3
def Fconectados(cont):  
    return  model.Fconectados(cont)
#req 4
def distanciaGeografica(analyzer, long1, lat1, long2, lat2):
    prohibidas = []
    copia_tabla_vertices = analyzer["vertices"]
    return model.distanciaGeografica(copia_tabla_vertices, analyzer, float(long1),float(lat1), float(long2), float(lat2), prohibidas)

#req 5
def estacionesAlcanzables(analyzer, origen, maxestaciones):
    return model.estacionesAlcanzables(analyzer, origen, maxestaciones)

# req 6 

def distanciaVecindario(analyzer, origen, vecindario):
    return model.distanciaVecindario(analyzer, origen,vecindario)
#req 6 ana
def distminestacion_vecindario(analyzer, estacion, vecindario):
    return model.distminestacion_vecindario(analyzer, estacion, vecindario)
def circular(cont,estacion):
    return model.circular(cont, estacion)
# Funciones print carga de datos 

def areaRectangular():
    lista_max_min = model.areaRectangular()
    #print(lista_max_min)
    return lista_max_min


def totalConnections(analyzer):
    """
    Total de enlaces entre las paradas
    """
    return model.totalConnections(analyzer)
    
def primerasyultimas5(analyzer):
    return model.primerasyultimas5(analyzer)

def crear_mapa(lista_long_lat, lista_identificadores,req):
    model.crear_mapa(lista_long_lat, lista_identificadores,req)