import requests
from random import randrange
import pandas as pd
import yfinance as yf
import time
from stockService import stocks


def getSuggestions(input):
    strats = input["strats"].split(",")
    products = input["products"].split(",")
    result = {}
    for product in products:
        for strat in strats:
            handler = handlerMap[product][strat]
            if handler != None:
                temp = handler(input)
                if len(result) == 0:
                    result = temp
                elif temp.keys()[0] not in result:
                    result.update(temp)
                else:
                    curTickers = result[temp.keys()[0]]["names"]
                    toAddTickers = temp[temp.keys()[0]]["names"]
                    result[temp.keys()[0]]["names"] = list(set(curTickers + toAddTickers))
    for key in result:
        result[key]["spend"] = (int)(input["amount"]) / len(result.keys())
    return result

# Large cap stocks


def value_selection(amount, stocks):
    # from the list of stocks, return top three and amount to each stocks
    # select from large cap stocks and choose one that suffered drop recently or traded sideways for a while
    # sp500 = get_sp500_tickers()

    return

stocks = grab_all_stocks()    

def get_growth_stocks(input):
    result={
        "stock": {
            "names" : [],
        },
    }
    temp = list(stocks.keys())
    temp = temp[:5]
    result["stock"]["names"] = temp
    return result

def get_value_stocks():
    # from the list of stocks, return top three and amount to each stocks
    # select from large cap stocks and choose one that suffered drop recently or traded sideways for a while
    val_stock = []
    index = randrange(500)
    sp500 = stocks['large']
    cnt = 0
    visited = []
    while len(val_stock) < 10:
        visited.append(index)
        s = sp500[index]
        info = yf.Ticker(s).info
        value_tick = 0
        if 'profitMargins' in info and info['profitMargins'] is not None and info['profitMargins'] >= 0.2:
            value_tick += 1
        if 'priceToBook' in info and info['priceToBook'] is not None and info['priceToBook'] <= 3:
            value_tick += 1
        if 'dividendRate' in info and info['dividendRate'] is not None:
            value_tick += 1
            
        # try to calculate eps
        
        if value_tick >= 2:
            val_stock.append(s)
        while index in visited:
            # print(visited, index)
            index = randrange(500)
        index += 1
    return val_stock

handlerMap = {
    "stock":{
        "ethical": None,
        "growth": get_growth_stocks,
        "quality": None,
        "index": None,
        "value": get_value_stocks,
    },
    "etf": {
        "ethical": None,
        "growth": None,
        "quality": None,
        "index": None,
        "value": None,
    },
}

