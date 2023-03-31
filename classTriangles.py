# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 10:11:20 2022

@author: 007xJ
"""

class Triangle:
    """
    
    IE: You have 500 BUSD. You go ETH/BUSD, 1000 BUSD for 1 ETH. You now have 0.5 ETH (balance / 1000)). Let's call this secondPrice
        You then go AVAX/ETH, 0.01 ETH for 1 AVAX. You now have 50 AVAX (secondPrice / 0.01). Let's call this thirdPrice
        You then go back to BUSD, AVAX/BUSD. 11 BUSD for 1 AVAX. You now have 550 BUSD (thirdPrice * 11). This is the finalPrice. 
        weight would now be equal to 1.1 (finalPrice/what you started with (500 BUSD))
        
    Example with volume:
        500 BUSD cash account. 
        ETH/BUSD at 1000, ask qty of 10 ETH (division)
        AVAX/ETH at 0.01, ask quantity of 40 AVAX (division)
        AVAX/BUSD at 11, bid quantity of 30 AVAX (multiplication)
            To find the minimum quantity: first off 500 BUSD, then we see there is a max of 10 ETH available. 10 * 1000 = 10,000 BUSD, more than
                our minimum starting balance, so now our minimum quantity is 0.5 ETH. 
            = (self.minimum) 0.5 ETH but only float(price[3]) 40 AVAX available. float(price[3])*float(price[2]) 40*0.01 = 0.4 ETH available. 
                Our new minimum is 40 AVAX
            = (self.minimum) 40 AVAX but only (float(price[3])) 30 AVAX available. 30 * 11 = 330 BUSD available. Our new minimum is now 330 BUSD
            We can therefore buy a maximum of 330 BUSD during the transaction.
    """
    def __init__(self, startingSymbol, startingPair, startingPrice, balance):
        """

        Parameters
        ----------
        startingPair : string
            pair you start with. in this case, ETH/BUSD
        startingPrice : float OR LIST
            tradingPrice, here it would be 1000
            if it is a list: will contain bidPrice, bidQty, askPrice, askQty all in string
        startingSymbol : string
            starting symbol you start with. in this case, it would be BUSD
        
        Returns
        -------
        None.

        """
        self.pairs = [startingPair]
        self.weight = 1.0
        self.symbol = startingSymbol
        self.quantities = []
        self.minimums = []
        self.balance = balance
        self.minimum = self.balance
        self.prices = []
        
        if (self.pairs[0].index(self.symbol) == 0): 
            self.currentPrice = self.balance * float(startingPrice[0]) # 1000 is present because we want to start with a default 1000
            self.prices.append(float(startingPrice[0]))
            self.symbol = self.pairs[0].split("/")[1]
            self.quantities.append(startingPrice[1] + self.symbol)
            if (self.balance > float(startingPrice[1])):
                self.minimum = float(startingPrice[1])
            else:
                self.minimum *= float(startingPrice[0])
            
        else: 
            self.currentPrice = self.balance / float(startingPrice[2])
            self.prices.append(float(startingPrice[2]))
            self.symbol = self.pairs[0].split("/")[0] # current fixing of the bug here, looking for right formula for minimum qty to buy
            self.quantities.append(startingPrice[3] + self.symbol)
            if (self.balance > float(startingPrice[3]) * float(startingPrice[2])):
                self.minimum = float(startingPrice[3]) * float(startingPrice[2])
            else: 
                self.minimum /= float(startingPrice[2])
                
        self.minimums.append(self.minimum)
        
        # since we have now transferred to another coin, we need to change the currentSymbol our portfolio is worth
    
    def append(self, pair, endingPair, priceToStarting, priceToEnd):
        """

        Parameters
        ----------
        pair : string
            next pair to be traded. in this case, this would be AVAX/ETH
        endingPair : string
            from the pair back to start. in this case, this would be AVAX/BUSD
        priceToStarting : float OR LIST
            we have ETH now, we want to go to AVAX. in this case, this would be 100
            if it is a list: will contain bidPrice, bidQty, askPrice, askQty all in string
        priceToEnd : float OR LIST
            we now have AVAX, we want to go to BUSD. in this case, this would be 11
            if it is a list: will contain bidPrice, bidQty, askPrice, askQty all in string

        Returns
        -------
        None.

        """
        self.pairs.append(pair)
        self.pairs.append(endingPair)
        
        if (self.pairs[1].index(self.symbol) == 0):
            self.currentPrice *= float(priceToStarting[0])
            self.prices.append(float(priceToStarting[0]))
            self.symbol = self.pairs[1].split("/")[1]
            self.quantities.append(priceToStarting[1] + self.symbol)
            
            if (self.minimum > float(priceToStarting[1])): # if ever the amount bid is smaller than what we had starting
                self.minimum = float(priceToStarting[1]) * float(priceToStarting[0])
            else:
                self.minimum *= float(priceToStarting[0]) # converting to the next coin
            
        else:
            self.currentPrice /= float(priceToStarting[2])
            self.prices.append(float(priceToStarting[2]))
            self.symbol = self.pairs[1].split("/")[0]
            self.quantities.append(priceToStarting[3] + self.symbol)
            
            if (self.minimum > float(priceToStarting[3]) * float(priceToStarting[2])):
                self.minimum = float(priceToStarting[3])
            else:
                self.minimum /= float(priceToStarting[2])
        
        self.minimums.append(self.minimum)
        
        if (self.pairs[2].index(self.symbol) == 0):
            self.currentPrice *= float(priceToEnd[0])
            self.prices.append(float(priceToEnd[0]))
            self.symbol = self.pairs[2].split("/")[1]
            self.quantities.append(priceToEnd[1] + self.symbol)
            
            if (self.minimum > float(priceToEnd[1])):
                self.minimum = float(priceToEnd[1]) * float(priceToEnd[0])
            else:
                self.minimum *= float(priceToEnd[0])

        else:
            self.currentPrice /= float(priceToEnd[2])
            self.prices.append(float(priceToEnd[2]))
            self.symbol = self.pairs[2].split("/")[0]
            self.quantities.append(priceToEnd[3] + self.symbol)
            
            if (self.minimum > float(priceToEnd[3]) * float(priceToEnd[2])):
                self.minimum = float(priceToEnd[3])
            else:
                self.minimum /= float(priceToEnd[2])
        
        self.minimums.append(self.minimum)
        
        self.weight = self.currentPrice / self.balance
    
    def getRoute(self):
        return self.pairs, self.weight, self.minimum, self.prices
    
    def __gt__(self, other):
        return 1/self.weight > 1/other.weight # priority queue gives to smallest: here, biggest weight = smallest number
        
        
        
# example from above!!      
# triangle = Triangle("BUSD", "ETH/BUSD", 1000)
# triangle.append("AVAX/ETH", "AVAX/BUSD", 0.01, 11)
