import requests
import random
import pandas as pd
import yfinance as yf
import time
from stockService import stocks, update


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
                elif list(temp.keys())[0] not in result:
                    result.update(temp)
                else:
                    curTickers = result[temp.keys()[0]]["names"]
                    toAddTickers = temp[temp.keys()[0]]["names"]
                    result[temp.keys()[0]]["names"] = list(set(curTickers + toAddTickers))
    for key in result:
        result[key]["spend"] = (int)(input["amount"]) / len(result.keys())
    return result

def get_growth_stocks(input):
    result={
        "stock": {
            "names" : [],
            "measures" : [],
        },
    }
    # msft = yf.Ticker("MSFT")
    # test = msft.earnings
    # print(test)
    # for i in range(4):
    #     print("i: ", i)
    #     print(test.iloc[-(i+1)]['Earnings'])
    for ticker in [key for key in stocks.keys() if key != "date"]:
        if "earnings" in stocks[ticker]:
            earnings = stocks[ticker]["earnings"]
            years = 3
            if len(earnings) >= years+1:
                qualified = True
                rateSum = 0.0
                for i in range(years):
                    prevYear = (int)(earnings.iloc[-(i+1)]['Earnings'])
                    prevPrev = (int)(earnings.iloc[-(i+2)]['Earnings'])
                    if (prevYear - prevPrev) / prevPrev < 0.15:
                        qualified = False
                        break
                    else:
                        rateSum += ((prevYear - prevPrev) / prevPrev)
                if qualified:
                    result["stock"]["names"].append(ticker)
                    result["stock"]["measures"].append(rateSum/years)
    print(result)
    return result

def get_value_stocks(input):
    # from the list of stocks, return top three and amount to each stocks
    # select from large cap stocks and choose one that suffered drop recently or traded sideways for a while
    val_stock = []

    visited = []
    ret = {}
    ticker = random.choice(list(stocks.keys()))
    products = input['products'].split(',')
    useStock = 'stock' in products
    useETF = 'etf' in products
    
    while len(val_stock) < 3:
        visited.append(ticker)
        s = stocks[ticker]

        value_tick = 0
        if 'info' in s:
            info = s['info']
            if info['marketCap'] > 2000000000:
                if 'profitMargins' in info and info['profitMargins'] is not None and info['profitMargins'] >= 0.2:
                    value_tick += 1
                if 'priceToBook' in info and info['priceToBook'] is not None and info['priceToBook'] <= 3:
                    value_tick += 1
                if 'dividendRate' in info and info['dividendRate'] is not None:
                    value_tick += 1

                # peg ratio to determine if stock is fairly valued
                if 'pegRatio' in info and info['pegRatio'] is not None and 1 >= info['pegRatio'] >= 0:
                    value_tick += 1
                            
                if value_tick >= 2:
                    val_stock.append(ticker)
        while ticker in visited:
            ticker = random.choice(list(stocks.keys()))
    if (useStock and useETF) :
        val_stock.pop()
        ret['stock'] = { 'names': val_stock}
    elif (useStock):
        ret['stock'] = { 'names': val_stock}
    else:
        ret['stock'] = {'names':[]}

    return ret

def get_value_eft(input):
    ret={
        "ETF": {
            "names" : [],
        },
    }
    """
        VYM has high divdend yields which makes it good value
        VTV tracks the value stocks
        SPY tracks SP500 which is always good value
    """
    etf = ['VYM', 'VTV', 'SPY']
    products = input['products'].split(',')
    useStock = 'stock' in products
    useETF = 'etf' in products
    if (useStock and useETF) :
        ret['ETF']['names'] = ['VTV'][:]
    elif (useETF):
        ret['ETF']['names'] =  etf[:]

    return ret

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
        "value": get_value_eft,
    },
}

