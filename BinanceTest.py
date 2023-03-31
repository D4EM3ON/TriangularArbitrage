# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 10:20:39 2022

@author: 007xJ
"""
import ccxt
import crypto
import numpy as np
from queue import PriorityQueue
from classTriangles import Triangle
import time
from buyingBinance import TradePath

exchange = ccxt.binance ()

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': crypto.getBinanceAPIKey(),
    'secret': crypto.getBinanceSecret(),
    'enableRateLimit': True,
})

startOverallTime = time.time()

def getAllActivePairs(exchange):
    """
    Parameters
    ----------
    exchange : CCXT exchange
        specific exchange we want to symbols of.

    Returns
    -------
    ex : dict
        bigger list with more accurate descriptions per symbol, with things like base asset, quote precision, etc.
    symbols : list
        list of active symbols.
    """
    exTemp = exchange.load_markets()
    
    ex = exTemp.copy()
    pairs = list()
    symbols = list()
    
    for key, value in exTemp.items():
        if not value.get('active') or value.get('info').get('status') == 'BREAK':
            ex.pop(key)
        else:
            pairs.append(key)
            symbol1, symbol2 = key.split("/")
            if symbol1 not in symbols: symbols.append(symbol1)
            if symbol2 not in symbols: symbols.append(symbol2)
    
    del(exTemp)
    
    return ex, pairs, symbols

def getMatrixSymbols(pairs, symbols):
    """
    Parameters
    ----------
    pairs : list
        1D list of all tradable pairs on a given exchange.
    symbols : dict
        1D list of all possible symbols on a given exchange as keys, and the index of them as a value

    Returns
    -------
    matrix : list
        2D list. 0 if there is no connection between two symbols, 1 if there is. It will be of size N x N, where N is the number of tradable coins

    """
    
    matrix = [[0]* len(symbols) for i in range(len(symbols))]
    matrixPair = [[0]* len(symbols) for i in range(len(symbols))]
    matrixPairList = []
    i = 0

    for pair in pairs:
        first, second = pair.split("/")
        
        first = symbols.get(first)
        second = symbols.get(second)
        
        matrix[first][second] = matrix[second][first] = 1
        matrixPair[first][second] = matrixPair[second][first] = i
        matrixPairList.append([first, second])
        i += 1
    
    return matrix, matrixPair, matrixPairList
    
def getTriangularTrade(matrix, symbols, arrSymbols, exchange, pairs, matrixPair, matrixPairList, balance, symbol):
    """
    Parameters
    ----------
    matrix : list
        2D list (graph) of all possible combinations/trading pairs. The rows and columns correspond to the symbols indexes
    symbols : dict
        Dictionary of all symbols as keys with their index of arrSymbols as value
    arrSymbols : NumPy array
        1D array of all possible symbols. to be used when dict is not convenient

    Returns
    -------
    

    """
    startTime = time.time()
    
    startingSymbol = symbol 
    startX = symbols.get(startingSymbol) 
    
    bestValue = PriorityQueue()
    triangles = list()
    
   
    allPrices = exchange.publicGetTickerBookticker()
        
    for pair in range(len(pairs)): 
        tempPair = pairs[pair].replace('/',"") # make them the same format as allPrices
        
        x, y = matrixPairList[pair]
        matrixPair[x][y] = matrixPair[y][x] = priceIndex.get(tempPair)
        allPrices[priceIndex.get(tempPair)]['symbol'] = pairs[pair]
    
    possibilities = list()
    for i in range(len(matrix[startX])):
        if matrix[startX][i] != 0:
            possibilities.append(i)
            
    possibilities2 = list() # possibilities2 is all possible triangular combinations, 2D, with place of 1D list first, and in that list is the second
    triangleCounter = 0
    for possibility in range(len(possibilities)):
        possibilityTemp = int(possibility)
        possibility = possibilities[possibility]
        
        possibilities2.append([])
        
        for i in range(len(matrix[possibility])):
            if (matrix[possibility][i] != 0 and matrix[startX][i] != 0):
                possibilities2[possibilityTemp].append(i)
                
                endDict = allPrices[matrixPair[startX][i]]
                endPair = endDict.get("symbol")
                endPrice = [endDict.get("bidPrice"), endDict.get("bidQty"), endDict.get("askPrice"), endDict.get("askQty")]
                
                
                nextDict = allPrices[matrixPair[possibility][i]]
                nextPair = nextDict.get("symbol")
                nextPrice = [nextDict.get("bidPrice"), nextDict.get("bidQty"), nextDict.get("askPrice"), nextDict.get("askQty")]
                
                startingDict = allPrices[matrixPair[startX][possibility]]
                startingPair = startingDict.get("symbol")
                startingPrice = [startingDict.get("bidPrice"), startingDict.get("bidQty"), startingDict.get("askPrice"), startingDict.get("askQty")]
                
                triangles.append(Triangle(startingSymbol, startingPair, startingPrice, balance))
                triangles[triangleCounter].append(nextPair, endPair, nextPrice, endPrice)
                
                bestValue.put(triangles[triangleCounter])
                
                
                # look every time for the weight, minimum and pairs
                bvPairs, bvWeight, bvMinimum, bvPrices = triangles[triangleCounter].getRoute()
                
                if (bvWeight >= 1.0023): 
                    print(bvPairs, bvWeight, bvMinimum, bvPrices)
                    if (bvMinimum > 20): bvMinimum = 20
                    tradingBinance.trade(bvPairs, bvPrices, bvMinimum, startingSymbol)

                triangleCounter += 1
                
    print("--- %s seconds ---" %(time.time()-startTime))

    return bestValue
    
ex, pairs, symbols = getAllActivePairs(exchange)

# print(exchange.public_get_ticker_price())
# print(exchange.public_get_ticker_bookticker())

arrSymbols = np.array(symbols)

symbols = {symbol : symbols.index(symbol) for symbol in symbols}
matrix, matrixPair, matrixPairList = getMatrixSymbols(pairs, symbols)
matrix = np.array(matrix)
priceIndex = dict()

priceIndex = dict()
allPrices = exchange.publicGetTickerBookticker()

for i in range(len(allPrices)):
    priceIndex[allPrices[i].get('symbol')] = i

counter = 0

tradingBinance = TradePath(exchange)
startingSymbol = "BUSD" # can be modified when you want to start with something else

while True:
    bestValue = getTriangularTrade(matrix, symbols, arrSymbols, exchange, pairs, matrixPair, matrixPairList, 40, startingSymbol)
    # for i in range(10): # print top 10
        # bvPairs, bvWeight, bvMinimum, bvPrices = bestValue.get().getRoute()
        # if (bvWeight >= 1.0023): print(bvPairs, bvWeight, bvMinimum, bvPrices)

        # if (bvMinimum >= 20 and bvWeight >= 1.0023):
            # tradingBinance.trade(bvPairs, bvPrices, 20, startingSymbol)
            # counter += 1
            # print(counter, "possibilities found in", time.time() - startOverallTime, "seconds")
            # break
    # print("")
    # print(counter, "possibilities found in", startOverallTime - time.time(), "seconds")
    # print()
    


























