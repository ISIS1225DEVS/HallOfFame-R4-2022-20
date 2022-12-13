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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
import csv
import re
import math
import folium
from folium.plugins import MarkerCluster
from DISClib.ADT import list as lt
from DISClib.ADT import orderedmap as om
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from datetime import datetime
from statistics import mean
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos
def newAnalyzer(structure):
    analyzer = {}
    analyzer['generalInformation'] = {}
    analyzer['videoGames'] = lt.newList(structure)
    analyzer['speedrunRecords'] = lt.newList(structure)
    analyzer['idVideoGames'] = mp.newMap(1100, maptype='PROBING')
    analyzer['releaseDates'] = om.newMap()
    analyzer['bestPlayers'] = mp.newMap(9500, maptype='PROBING')
    analyzer['Num_Runs'] = om.newMap()
    analyzer['recordDates'] = om.newMap()
    analyzer['Time_0'] = om.newMap(omaptype="RBT", comparefunction=compareTimes)
    analyzer['releaseYears'] = om.newMap()
    analyzer['platforms'] = mp.newMap(150, maptype='PROBING')
    return analyzer

# Funciones para agregar informacion al catalogo
def addRegister(analyzer, register, type):
    if type == 'game':
        register = updateGeneralInformation(analyzer, register, 'game')
        addIdVideoGames(analyzer, register)
        addReleaseDate(analyzer, register)
        lt.addLast(analyzer['videoGames'], register)
    else:
        register = conectGamesId(analyzer, register)
        register = updateGeneralInformation(analyzer, register, 'speedrun')
        addBestPlayer(analyzer, register)
        addRecordDate(analyzer, register)
        addReleaseYear(analyzer, register)
        addAttempsByGame(analyzer, register)
        addTime0(analyzer, register)
        addPlatforms(analyzer, register, revenue=True)
        lt.addLast(analyzer['speedrunRecords'], register)
    return analyzer

def updateGeneralInformation(analyzer, register, type):
    if type == 'game':
        platforms = register['Platforms'].split(', ')
        for platform in platforms:
            platform = platform.title()
            countPlatform = analyzer['generalInformation'].get(platform, 0)
            analyzer['generalInformation'][platform] = countPlatform + 1
        date = register['Release_Date']
        if date == '':
            date = 'Unknown'
        else:
            date = datetime.strptime(date, '%y-%m-%d')
            date = date.strftime("%Y-%m-%d")
        register['Release_Date'] = date
    else:
        date = register['Record_Date_0']
        if date == '':
            date = 'Unknown'
        else:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        register['Record_Date_0'] = date
    return register

def conectGamesId(analyzer, register):
    GameId = register['Game_Id']
    entry = mp.get(analyzer['idVideoGames'], GameId)
    if entry:
        videoGame = me.getValue(entry)
        register['Name'] = videoGame['Name']
        register['Platforms'] = videoGame['Platforms']
        register['Genres'] = videoGame['Genres']
        register['Release_Date'] = videoGame['Release_Date']
        register['Total_Runs'] = videoGame['Total_Runs']
    return register

def addIdVideoGames(analyzer, register):
    GameId = register['Game_Id']
    entry = mp.get(analyzer['idVideoGames'], GameId)
    if entry is None:
        mp.put(analyzer['idVideoGames'], GameId, register)

def addReleaseDate(analyzer, register):
    releaseDate = register['Release_Date']
    if releaseDate != 'Unknown':
        releaseDate = datetime.strptime(releaseDate, "%Y-%m-%d")
        entry = om.get(analyzer['releaseDates'], releaseDate)
        if entry is None:
            date = newReleaseDate(releaseDate)
            om.put(analyzer['releaseDates'], releaseDate, date)
        else:
            date = me.getValue(entry)
        addPlatforms(date, register)

def addBestPlayer(analyzer, register):
    players = re.split(',|, ', register['Players_0'])
    for player in players:
        entry = mp.get(analyzer['bestPlayers'], player)
        if entry is None:
            bestPlayer = newBestPlayer(player)
            mp.put(analyzer['bestPlayers'], player, bestPlayer)
        else:
            bestPlayer = me.getValue(entry)
        lt.addLast(bestPlayer['registers'], register)
        bestPlayer['generalInformation']['attemps'] += int(register['Num_Runs'])

def addAttempsByGame(analyzer, register):
    attemps = int(register['Num_Runs'])
    entry = om.get(analyzer['Num_Runs'], attemps)
    if entry is None:
        AttempsByGame = newFasterRecord(attemps)
        om.put(analyzer['Num_Runs'], attemps, AttempsByGame)
    else:
        AttempsByGame = me.getValue(entry)
    lt.addLast(AttempsByGame['registers'], register)

def addRecordDate(analyzer, register):
    date = register['Record_Date_0']
    if date != 'Unknown':
        entry = om.get(analyzer['recordDates'], date)
        if entry is None:
            recordDate = newRecordDate(date)
            om.put(analyzer['recordDates'], date, recordDate)
        else:
            recordDate = me.getValue(entry)
        lt.addLast(recordDate['registers'], register)

def addTime0(analyzer, register):
    time0 = float(register['Time_0'])
    entry = om.get(analyzer['Time_0'], time0)
    if entry is None:
        categorias = lt.newList()
        lt.addLast(categorias, register)
        om.put(analyzer['Time_0'], time0, categorias)
    else:
        pre = om.get(analyzer['Time_0'], time0)
        categorias_2 = me.getValue(pre)
        lt.addLast(categorias_2, register)
        om.put(analyzer['Time_0'], time0, categorias_2)

def addReleaseYear(analyzer, register):
    rYear = register['Release_Date']
    if rYear != 'Unknown':
        rYear = datetime.strptime(rYear, "%Y-%m-%d").year
        entry = om.get(analyzer['releaseYears'], rYear)
        if entry is None:
            releaseYear = newReleaseYear(rYear)
            om.put(analyzer['releaseYears'], rYear, releaseYear)
        else:
            releaseYear = me.getValue(entry)
        lt.addLast(releaseYear['registers'], register)
        addCountries(releaseYear, register)

def addPlatforms(analyzer, register, revenue=False):
    if revenue:
        register = calculateRevenue(register)
    if register is not None:
        platforms = register['Platforms'].split(', ')
        for platformName in platforms:
            platformName = platformName.title()
            entry = mp.get(analyzer['platforms'], platformName)
            if entry is None:
                platform = newPlatform(platformName)
                mp.put(analyzer['platforms'], platformName, platform)
            else:
                platform = me.getValue(entry)
            lt.addLast(platform['registers'], register)
            if revenue:
                addRecordsByGame(platform, register)

def addRecordsByGame(analyzer, register):
    gameId = register['Game_Id']
    entry = mp.get(analyzer['records'], gameId)
    if entry is None:
        game = newGame(gameId)
        mp.put(analyzer['records'], gameId, game)
    else:
        game = me.getValue(entry)
    lt.addLast(game['registers'], register)

def addCountries(analyzer, register):
    countryNames = re.split(',|, ', register['Country_0'])
    for countryName in countryNames:
        entry = mp.get(analyzer['countries'], countryName)
        if entry is None:
            country = newCountry(countryName)
            mp.put(analyzer['countries'], countryName, country)
        else:
            country = me.getValue(entry)
        addBestTimes(country, register)

def addBestTimes(analyzer, register):
    time = float(register['Time_0'])
    entry = om.get(analyzer['bestTimes'], time)
    if entry is None:
        bestTime = newBestTime(time)
        om.put(analyzer['bestTimes'], time, bestTime)
    else:
        bestTime = me.getValue(entry)
    lt.addLast(bestTime['registers'], register)

# Funciones para creacion de datos
def newReleaseDate(releaseDate):
    date = {}
    date['releaseDate'] = releaseDate
    date['platforms'] = mp.newMap(150, maptype='PROBING')
    return date

def newBestPlayer(player):
    bestPlayer = {}
    bestPlayer['player'] = player
    bestPlayer['registers'] = lt.newList()
    bestPlayer['generalInformation'] = {'attemps': 0}
    return bestPlayer

def newFasterRecord(attemp):
    FasterRecord = {}
    FasterRecord['attemp'] = attemp
    FasterRecord['registers'] = lt.newList()
    return FasterRecord

def newRecordDate(date):
    recordDate = {}
    recordDate['date'] = date
    recordDate['registers'] = lt.newList()
    return recordDate

def newBestTime(time):
    bestTime = {}
    bestTime['time'] = time
    bestTime['registers'] = lt.newList()
    return bestTime

def newCountry(countryName):
    country = {}
    country['country'] = countryName
    country['bestTimes'] = om.newMap()
    return country

def newReleaseYear(year):
    releaseYear = {}
    releaseYear['year'] = year
    releaseYear['registers'] = lt.newList()
    releaseYear['countries'] = mp.newMap(maptype='PROBING')
    return releaseYear

def newPlatform(platformName):
    platform = {}
    platform['platform'] = platformName
    platform['registers'] = lt.newList()
    platform['records'] = mp.newMap()
    return platform

def newGame(gameName):
    game = {}
    game['game'] = gameName
    game['registers'] = lt.newList()
    return game

# Funciones de consulta
def getGamesByPlatformInDate(analyzer, platform, initialDate, finalDate):
    filtered = lt.newList()
    details = {'gamesByPlatform': analyzer['generalInformation'].get(platform, 0), 'gamesInRange': 0}
    releaseDates = om.keys(analyzer['releaseDates'], initialDate, finalDate)
    for releaseDate in lt.iterator(releaseDates):
        entry = om.get(analyzer['releaseDates'], releaseDate)
        platforms = me.getValue(entry)['platforms']
        gamesByPlatform = mp.get(platforms, platform)
        if gamesByPlatform:
            games = me.getValue(gamesByPlatform)['registers']
            sortRegisters(games, compareReq1)
            date = {'Release_Date': releaseDate.strftime("%Y-%m-%d"), 'Details': games, 'Count': lt.size(games)}
            details['gamesInRange'] += lt.size(games)
            lt.addLast(filtered, date)
    sortRegisters(filtered, compareReleaseDate)
    return filtered, details

def getRegistersByPlayer(analyzer, player):
    filtered = lt.newList()
    details = {'attempsByPlayer': 0}
    entry = mp.get(analyzer['bestPlayers'], player)
    if entry:
        player = me.getValue(entry)
        filtered = player['registers']
        details['attempsByPlayer'] = player['generalInformation']['attemps']
    sortRegisters(filtered, compareReq2)
    filteredData = lt.newList()
    if lt.size(filtered) <= 5:
        filteredData = filtered
    else:
        for i in range(1, 6):
            register = lt.removeFirst(filtered)
            register['Rank'] = i
            lt.addLast(filteredData, register)
    return filteredData, details

def getFasterRecords(analyzer,lim_inf, lim_sup):
    filtered = lt.newList()
    details = {'Total_attemps': 0}
    attemps = om.keys(analyzer['Num_Runs'], lim_inf,lim_sup)
    for attemp in lt.iterator(attemps):
        entry= om.get(analyzer['Num_Runs'], attemp)
        registers = me.getValue(entry)['registers']
        sortRegisters(firstAndLastThreeData(registers), compareReq3)
        data = {'Num_Runs': attemp, 'Count': lt.size(registers), 'Details': registers}
        details['Total_attemps']+= lt.size(registers)
        lt.addLast(filtered, data)
    return filtered, details

def getRegistersByDates(analyzer, initialDate, finalDate):
    filered = lt.newList()
    dates = om.keys(analyzer['recordDates'], initialDate, finalDate)
    details = {'totalRecords': lt.size(dates)}
    dates = firstAndLastThreeData(dates)
    for date in lt.iterator(dates):
        entry = om.get(analyzer['recordDates'], date)
        registers = me.getValue(entry)['registers']
        sortRegisters(registers, compareReq4)
        recordDate = {'Record_Date_0': date, 'Details': registers, 'Count': lt.size(registers)}
        lt.addLast(filered, recordDate)
    sortRegisters(filered, compareBestRecordDate)
    return filered, details

def getRegistersByRange(analyzer, minTime, maxTime):
    filtered = lt.newList()
    details = {'No. Records': 0}
    times = om.keys(analyzer["Time_0"], minTime, maxTime)
    details["Number of elements"] = lt.size(times)
    details["Times"] = lt.newList()
    details["Number of records"] = 0
    for time in lt.iterator(times):
        values = om.get(analyzer["Time_0"], time)
        entries = me.getValue(values)
        lt.addLast(details["Times"], {"Tiempo": time, "Count" : lt.size(entries)})
        time_0 = {'Time_0': time, 'Details': entries, 'Count': lt.size(entries)}
        details['No. Records'] += lt.size(entries)
        lt.addLast(filtered, time_0)
        details["Number of records"] += 1
    return filtered, details

def histogramByReleaseYears(analyzer, initialYear, finalYear, feature, numberSegments, numberLevels):
    filtered = lt.newList()
    details = {'consultedAttemps': 0, 'includedRegisters': 0}
    counts = []
    years = om.keys(analyzer['releaseYears'], initialYear, finalYear)
    for year in lt.iterator(years):
        entry = om.get(analyzer['releaseYears'], year)
        registers = me.getValue(entry)['registers']
        for register in lt.iterator(registers):
            details['consultedAttemps'] += 1
            item = determinateItem(register, feature)
            if item is not None:
                details['includedRegisters'] += 1
                highest = details.get('highest', item)
                lowest = details.get('lowest', item)
                if item > highest:
                    highest = item
                details['highest'] = highest
                if item < lowest:
                    lowest = item
                details['lowest'] = lowest
                counts.append(item)
    createPocketForHistogram(filtered, details, counts, numberSegments, numberLevels)
    return filtered, details

def getTopNByProfitableVideogamesInPlatform(analyzer, platform, N):
    filtered = lt.newList()
    details = {'gamesByPlatform': analyzer['generalInformation'].get(platform, 0), 'registersInRange': 0}
    entry = mp.get(analyzer['platforms'], platform)
    if entry:
        node = me.getValue(entry)
        totalRegisters = lt.size(node['registers'])
        details['registersInRange'] = totalRegisters
        records = node['records']
        games = mp.keySet(records)
        for gameId in lt.iterator(games):
            entryGame = mp.get(records, gameId)
            registers = me.getValue(entryGame)['registers']
            game = getGame(analyzer, gameId)
            game['Market_Share'] = lt.size(registers) / totalRegisters
            for register in lt.iterator(registers):
                game['Stream_Revenue'] += (register['revenue'] * game['Market_Share'])
                game['Time_Avg'].append(register['Time_Avg'])
            game['Time_Avg'] = round(mean(game['Time_Avg']), 2)
            game['Market_Share'] = round(game['Market_Share'], 2)
            game['Stream_Revenue'] = round(game['Stream_Revenue'], 2)
            lt.addLast(filtered, game)
    sortRegisters(filtered, compareRevenue)
    topN = lt.newList()
    if N > lt.size(filtered):
        N = lt.size(filtered)
    for i in range(1, N+1):
        register = lt.removeFirst(filtered)
        register['Rank'] = i
        lt.addLast(topN, register)
    return topN, details

def graphAttempsByCountriesInRangeOfYears(analyzer, year, timeInf, timeSup):
    filtered = lt.newList()
    details = {'registersInRange': 0, 'Map': None}
    entry = om.get(analyzer['releaseYears'], year)
    if entry:
        map = folium.Map(location=[0,0], zoom_start=2)
        mark = MarkerCluster()
        coordinates = loadCoordinates()
        countries = me.getValue(entry)['countries']
        for countryName in lt.iterator(mp.keySet(countries)):
            if countryName in coordinates.keys():
                coordinatesCountry = coordinates[countryName]
                country = {'Country': countryName, 'Count': 0, 'Details': lt.newList(), 'Coordinates': [float(coordinatesCountry['Latitude']), float(coordinatesCountry['Longitude'])]}
                entryCountry = mp.get(countries, countryName)
                bestTimes = me.getValue(entryCountry)['bestTimes']
                for bestTime in lt.iterator(om.keys(bestTimes, timeInf, timeSup)):
                    entryBestTime = om.get(bestTimes, bestTime)
                    registers = me.getValue(entryBestTime)['registers']
                    country['Count'] += lt.size(registers)
                    details['registersInRange'] += lt.size(registers)
                    for register in lt.iterator(registers):
                        lt.addLast(country['Details'], register)
                        mark.add_child(folium.Marker(location=country['Coordinates'], popup='Time_0: {0}\nPlayers_0: {1}\nName: {2}\nRelease_Date: {3}\nCountry: {4}'.format(register['Time_0'], register['Players_0'], register['Name'], register['Release_Date'], register['Country_0'])))
                if country['Count'] > 0:
                    lt.addLast(filtered, country)
        map.add_child(mark)
        map.save('Map.html')
        details['Map'] = True
    sortRegisters(filtered, compareCounts)
    return filtered, details

# Funciones de soporte para las consultas
def createPocketForHistogram(filtered, details, counts, numberSegments, numberLevels):
    if (len(details) > 2) and (numberSegments > 0) and (numberLevels > 0):
        period = (details['highest'] - details['lowest']) / numberSegments
        lastRangeA = details['lowest']
        for number in range(1, numberSegments + 1):
            data = {}
            lastRangeB = round(((period * number) + details['lowest']), 2)
            count = 0
            for item in counts:
                if (item + 0.01 > lastRangeA) and (item <= lastRangeB):
                    count += 1
            data['bin'] = '({0}, {1}]'.format(lastRangeA, lastRangeB)
            data['count'] = count
            data['lvl'] = count // numberLevels
            if data['lvl'] == 0:
                data['mark'] = ' '
            else:
                data['mark'] = '*' * data['lvl']
            lastRangeA = lastRangeB
            lt.addLast(filtered, data)
    else:
        details['lowest'] = None
        details['highest'] = None

def determinateItem(register, feature):
    item = None
    if (feature == 'Best Time') and (register['Time_0'] != ''):
        item = float(register['Time_0'])
    elif (feature == 'Second Best Time') and (register['Time_1'] != ''):
        item = float(register['Time_1'])
    elif (feature == 'Third Best Time') and (register['Time_2'] != ''):
        item = float(register['Time_2'])
    elif (feature == 'Average Time'):
        times = [float(register['Time_0'])]
        if register['Time_1'] != '':
            times.append(float(register['Time_1']))
        if register['Time_2'] != '':
            times.append(float(register['Time_2']))
        item = round(mean(times), 2)
    elif (feature == 'Number Runs') and (register['Num_Runs'] != ''):
        item = int(register['Num_Runs'])
    return item

def calculateRevenue(register):
    if register['Misc'] == 'False':
        rYear = datetime.strptime(register['Release_Date'], "%Y-%m-%d").year
        if rYear >= 2018:
            antiquity = rYear - 2017
        elif (rYear >= 1998) and (rYear < 2018):
            antiquity = (-(1/5) * rYear) + 404.6
        else:
            antiquity = 5
        popularity = math.log(int(register['Total_Runs']))
        times = [float(register['Time_0'])]
        if register['Time_1'] != '':
            times.append(float(register['Time_1']))
        if register['Time_2'] != '':
            times.append(float(register['Time_2']))
        timeAvg = mean(times)
        revenue = (popularity * (timeAvg / 60)) / antiquity
        register['Time_Avg'] = timeAvg
        register['revenue'] = revenue
    else:
        register = None
    return register

def loadCoordinates():
    coordinates = {}
    contentFile = cf.data_dir + 'Coordinates//Coordinates.csv'
    inputFile = csv.DictReader(open(contentFile, encoding="utf-8"), delimiter=",")
    for country in inputFile:
        coordinates[country['Country']] = country
    return coordinates

def getGame(analyzer, gameId):
    game = mp.get(analyzer['idVideoGames'], gameId)
    game = me.getValue(game)
    game['Stream_Revenue'] = 0
    game['Time_Avg'] = []
    return game

# Funciones utilizadas para comparar elementos dentro de una lista
def compareReq1(register1, register2):
    if register1['Release_Date'] == register2['Release_Date']:
        if register1['Abbreviation'] == register2['Abbreviation']:
            return compareName(register1, register2)
        else:
            return compareAbbreviation(register1, register2)
    else:
        return compareReleaseDate(register1, register2)

def compareReq2(register1, register2):
    if register1['Time_0'] == register2['Time_0']:
        if register1['Record_Date_0'] == register2['Record_Date_0']:
            return compareName(register1, register2)
        else:
            return compareBestRecordDate(register1, register2)
    else:
        return compareBestTime(register1, register2)

def compareReq3(register1, register2):
    if register1['Time_0'] == register2['Time_0']:
        if register1['Record_Date_0'] == register2['Record_Date_0']:
            return compareName(register1, register2)
        else:
            return compareBestRecordDate(register1, register2)
    else:
        return not compareBestTime(register1, register2)

def compareReq4(register1, register2):
    if register1['Time_0'] == register2['Time_0']:
        if register1['Num_Runs'] == register2['Num_Runs']:
            return compareName(register1, register2)
        else:
            return compareNumRums(register1, register2)
    else:
        return compareBestTime(register1, register2)

def compareName(register1, register2):
    return (register1['Name'] < register2['Name'])

def compareAbbreviation(register1, register2):
    return (register1['Abbreviation'] < register2['Abbreviation'])

def compareReleaseDate(register1, register2):
    date1 = datetime.strptime(register1['Release_Date'], '%Y-%m-%d')
    date2 = datetime.strptime(register2['Release_Date'], '%Y-%m-%d')
    return (date1 > date2)

def compareBestTime(register1, register2):
    return (float(register1['Time_0']) < float(register2['Time_0']))

def compareBestRecordDate(register1, register2):
    if (type(register1['Record_Date_0']) != str) and (type(register2['Record_Date_0']) != str):
        return (register1['Record_Date_0'] > register2['Record_Date_0'])

def compareNumRums(register1, register2):
    return (int(register1['Num_Runs']) < int(register2['Num_Runs']))

def compareRevenue(register1, register2):
    return (float(register1['Stream_Revenue']) > float(register2['Stream_Revenue']))

def compareCounts(register1, register2):
    return (int(register1['Count']) > int(register2['Count']))

def compareTimes(time1, time2):
    """
    Compara dos tiempos
    """
    time1 = float(time1)
    time2 = float(time2)
    if (time1 == time2):
        return 0
    elif (time1 > time2):
        return 1
    else:
        return -1

# Funciones de ordenamiento
def firstAndLastThreeData(lista):
    filteredData = lt.newList()
    size = lt.size(lista)
    if size >= 1:
        if size <= 5:
            filteredData = lista
        else:
            for pos in range(1, 4):
                data = lt.getElement(lista, pos)
                lt.addLast(filteredData, data)
            for pos in range(size-2, size+1):
                data = lt.getElement(lista, pos)
                lt.addLast(filteredData, data)
    return filteredData

def sortRegisters(lista, compareReq):
    return sa.sort(lista, compareReq)