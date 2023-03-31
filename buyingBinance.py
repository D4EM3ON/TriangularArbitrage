# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 18:03:30 2022

@author: 007xJ
"""
import crypto
import numpy as np
import ccxt

# rounding mode
TRUNCATE = 0
ROUND = 1
ROUND_UP = 2
ROUND_DOWN = 3

# digits counting mode
DECIMAL_PLACES = 2
SIGNIFICANT_DIGITS = 3
TICK_SIZE = 4

# padding mode
NO_PADDING = 5
PAD_WITH_ZERO = 6


class TradePath:
    def __init__(self, exchange):
        self.exchange = exchange
        self.decimals = crypto.getDecimals()
        # exchangeInfo = exchange.publicGetExchangeInfo()
        
    def trade(self, paths, prices, quantity, startCurrency):
        self.start = 0
        self.paths = paths
        self.prices = prices
        self.quantity = quantity
        self.currency = startCurrency
        for i in range(len(paths)):
            path = paths[i]
            if path.index(self.currency) == 0: # we would be selling
                self.currency = path.split("/")[1]
                print("selling", self.currency, self.quantity, self.prices[i])
                trade = self.exchange.createLimitSellOrder(path, self.quantity, self.prices[i])
                
                if i == 0: self.start = float(self.quantity) / float(self.prices[i])
                
                if (trade["status"] == "open"):
                    self.exchange.editOrder(trade["info"]["orderId"], path, "market", "sell", float(trade["info"]["origQty"]) - float(trade["info"]["executedQty"]))
                    
                self.quantity = float(trade["info"]["origQty"]) * float(trade["info"]["price"])
                            
            else: # we would be buying
                try:
                    decimalPlace = self.decimals[path.replace("/","")]
                    
                    val = np.longdouble(self.quantity)/np.longdouble(prices[i])
                    self.quantity = np.longdouble(ccxt.decimal_to_precision(val, TRUNCATE, decimalPlace, DECIMAL_PLACES))
                                    
                    self.currency = path.split("/")[0]
                    print("buying", self.currency, self.quantity, self.prices[i])
                    
                    if i == 0: self.start = float(self.quantity) * float(self.prices[i])
                    
                    trade = self.exchange.createLimitBuyOrder(path, self.quantity, self.prices[i])
                    
                    if (trade["status"] == "open"):
                        self.exchange.editOrder(trade["info"]["orderId"], path, "market", "buy", float(trade["info"]["origQty"]) - float(trade["info"]["executedQty"]))
                        
                    self.quantity = float(trade["amount"])
                except:
                    continue
            print(trade)
        print("started with", self.start, "and ended with", self.quantity)
        
        
# import math
# exchangeInfo = exchange.publicGetExchangeInfo()["symbols"]
# decimalsPerSymbol = dict()
# for symbol in exchangeInfo:
#     decimalsPerSymbol[symbol["symbol"]] = round(abs(math.log(float(symbol["filters"][0]["tickSize"]), 10)))