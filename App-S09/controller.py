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
from datetime import datetime

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
    contentFile = cf.data_dir + 'Speedruns//game_data_utf-8-' + str(sizeFile) + '.csv'
    inputFile = csv.DictReader(open(contentFile, encoding="utf-8"), delimiter=",")
    for game in inputFile:
        model.addRegister(analyzer, game, 'game')
    contentFile = cf.data_dir + 'Speedruns//category_data_utf-8-' + str(sizeFile) + '.csv'
    inputFile = csv.DictReader(open(contentFile, encoding="utf-8"), delimiter=",")
    for register in inputFile:
        model.addRegister(analyzer, register, 'speedrun')

# Funciones de ordenamiento
def firstAndLastThreeData(lista):
    return model.firstAndLastThreeData(lista)

# Funciones de consulta sobre el catálogo
def getGamesByPlatformInDate(analyzer, platform, initialDate, finalDate):
    platform = platform.title()
    initialDate = datetime.strptime(initialDate, '%Y-%m-%d')
    finalDate = datetime.strptime(finalDate, '%Y-%m-%d')
    return model.getGamesByPlatformInDate(analyzer, platform, initialDate, finalDate)

def getRegistersByPlayer(analyzer, player):
    player = player.title()
    return model.getRegistersByPlayer(analyzer, player)

def getFasterRecords(analyzer,lim_inf, lim_sup):
    return model.getFasterRecords(analyzer,lim_inf, lim_sup)

def getRegistersByDates(analyzer, initialDate, finalDate):
    initialDate = datetime.strptime(initialDate, '%Y-%m-%dT%H:%M:%SZ')
    finalDate = datetime.strptime(finalDate, '%Y-%m-%dT%H:%M:%SZ')
    return model.getRegistersByDates(analyzer, initialDate, finalDate)

def getRegistersByRange(analyzer, minTime, maxTime):
    return model.getRegistersByRange(analyzer, minTime, maxTime)

def histogramByReleaseYears(analyzer, initialYear, finalYear, feature, numberSegments, numberLevels):
    return model.histogramByReleaseYears(analyzer, initialYear, finalYear, feature, numberSegments, numberLevels)

def getTopNByProfitableVideogamesInPlatform(analyzer, platform, N):
    platform = platform.title()
    return model.getTopNByProfitableVideogamesInPlatform(analyzer, platform, N)

def graphAttempsByCountriesInRangeOfYears(analyzer, year, timeInf, timeSup):
    return model.graphAttempsByCountriesInRangeOfYears(analyzer, year, timeInf, timeSup)

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
