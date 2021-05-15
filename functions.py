import requests
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

handlerMap = {
    "stock":{
        "ethical": None,
        "growth": get_growth_stocks,
        "quality": None,
        "index": None,
        "value": None,
    },
    "etf": {
        "ethical": None,
        "growth": None,
        "quality": None,
        "index": None,
        "value": None,
    },
}

