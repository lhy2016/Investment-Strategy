from numpy.testing._private.utils import measure
import requests
import random
import pandas as pd
import yfinance as yf
import time
from stockService import stocks, update
import investpy as ipy


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


def get_etf_names_by_symbols(symbolList):
    allETFs = ipy.get_etfs_dict(columns=["name","symbol"])
    result = [None]*len(symbolList)
    for obj in allETFs:
        if obj['symbol'] in symbolList:
            index = symbolList.index(obj['symbol'])
            result[index] = obj['name']
    return [x for x in result if x != None]
    
    
def get_growth_etfs(input):
    result={
        "ETF": {
            "names" : [],
            "measures" : [],
        },
    }
 
    etf = ["TQQQ", "TECL", "ROM", "ARKG", "SOXL", "QLD", "ARKW", "ARKK", "IBUY", "FBGX", "FLGE", "FRLG", "ARKQ", "SMOG", "XSD", "SMH", "USD", "SOXX", "CURE", "UCC", "XITK", "PTF", "PSI", "PSJ", "VGT"]
    names = get_etf_names_by_symbols(etf)
    print(names)
    return result

def get_growth_stocks(input):
    result={
        "stock": {
            "names" : [],
            "measures" : [],
        },
    }
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
    return result

def get_value_stocks(input):
    # from the list of stocks, return top three and amount to each stocks
    # select from large cap stocks and choose one that suffered drop recently or traded sideways for a while
    val_stock = []
    measures = [0, 0, 0]
    pegRatio = []
    visited = []
    ret={
        "stock": {
            "names" : [],
            "measures" : [],
        },
    }
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
                    if 'pegRatio' in info and info['pegRatio'] is not None:
                        pegRatio.append(info['pegRatio'])
                    else:
                        pegRatio.append(99999999999)

                    # measures.append(value_tick)
        while ticker in visited:
            ticker = random.choice(list(stocks.keys()))
    """
        determin allocation of stocks
        stocks with smallest peg is given most allocation
        other are equally allocated
    """
    smallestPeg = min(pegRatio)
    indexSmallestPeg = pegRatio.index(smallestPeg)
            
    if (useStock and useETF) :
        if smallestPeg == 99999999999:
            measures = [0.25, 0.25, 0.25]
        else:
            for i in range(len(measures)):
                if i == indexSmallestPeg:
                    measures[i] = 0.35
                else:
                    measures[i] = 0.2
        ret['stock']['names'] =  val_stock
        ret['stock']['measures'] = measures[:]
    elif (useStock):
        if smallestPeg == 99999999999:
            measures = [0.25, 0.25, 0.25]
        else:
            for i in range(measures):
                if i == indexSmallestPeg:
                    measures[i] = 0.7
                else:
                    measures[i] = 0.15
        ret['stock']['names'] =  val_stock
        ret['stock']['measures'] = measures[:]
    return ret

def get_value_eft(input):
    ret={
        "ETF": {
            "names" : [],
            "measures" : [],
        },
    }
    """
        VYM has high divdend yields which makes it good value
        VTV tracks the value stocks
        SPY tracks SP500 which is always good value
    """
    etf = ['VYM', 'VTV', 'SPY']
    measures = [0.25, 0.5, 0.25]
    products = input['products'].split(',')
    useStock = 'stock' in products
    useETF = 'etf' in products
    if (useStock and useETF) :
        ret['ETF']['names'] = ['VTV'][:]
        ret['ETF']['measures'] = [0.25]
    elif (useETF):
        ret['ETF']['names'] =  etf[:]
        ret['ETF']['names'] = measures[:]
    return ret

def get_index_stocks(input):
    res = {}
    '''
    For index strategy, we are using annualReportExpenseRatio as metric. The lower the expenseRatio, the better the stock.

    source: 
    https://www.forbes.com/advisor/retirement/best-total-stock-market-index-funds/
    https://www.bankrate.com/investing/best-index-funds/
    The following index fund are good index stocks because they have low expense ratio and considerable 5 year return
    FNILX
    SWPPX
    SWTSX
    VTSAX
    FZROX
    FSKAX
    VRTTX
    WFIVX
    '''
    tickers = ['FNILX', 'SWPPX', 'SWTSX', 'VTSAX', 'FZROX', 'FSKAX', 'VRTTX', 'WFIVX']
    #tickers = list(stocks.keys())
    print (tickers)

    products = input['products'].split(',')
    useStock = 'stock' in products
    useETF = 'etf' in products

    selected_tickers = []
    measures = []
    stock_dic = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        if 'annualReportExpenseRatio' in info and info['annualReportExpenseRatio'] is not None:
            print (f'ticker has annualReportExpenseRatio: {ticker}, annualReportExpenseRatio is {info["annualReportExpenseRatio"]}')
            if info['annualReportExpenseRatio'] <= 0.01:
                stock_dic[ticker] = info['annualReportExpenseRatio']
            
    sort_stocks = sorted(stock_dic.items(), key=lambda x: x[1])
    for s in sort_stocks:
        if len(selected_tickers) <=2:
            selected_tickers.append(s[0])
            measures.append(s[1])  
    print (selected_tickers) 
    print (measures)      

    print (f'number of select tickers is {len(selected_tickers)}')
    if (useStock and useETF) :
        selected_tickers.pop()
        measures.pop()
        res["stock"] = { "names": selected_tickers}
        res["stock"] = { "measures": measures}
    elif (useStock):
        res["stock"] = { 'names': selected_tickers}
        res["stock"] = { 'measures': measures}
    else:
        res["stock"] = { "names": []}
        res["stock"] = { "measures": []}
    return res

def get_index_eft(input):
    res={
        "etf": {
            "names" : [],
        },
    }
    '''
    source: https://www.bankrate.com/investing/best-index-funds/
    VOO: expense ratio = 0.03%
    SPY: expense ratio = 0.09%
    IVV: expense ratio = 0.03%
    '''
    etf = ['VOO', 'SPY', 'IVV']
    products = input['products'].split(',')
    useStock = 'stock' in products
    useETF = 'etf' in products
    return res

handlerMap = {
    "stock":{
        "ethical": None,
        "growth": get_growth_stocks,
        "quality": None,
        "index": get_index_stocks,
        "value": get_value_stocks,
    },
    "etf": {
        "ethical": None,
        "growth": get_growth_etfs,
        "quality": None,
        "index": get_index_eft,
        "value": get_value_eft,
    },
}

