from numpy.testing._private.utils import measure
import requests
import random
import pandas as pd
import yfinance as yf
import time
from stockService import stocks, update
import investpy as ipy
from datetime import datetime


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
    return result
    
    
def get_growth_etfs(input):
    result={
        "ETF": {
            "names" : [],
            "measures" : [],
        },
    }
 
    etf = [ {"TQQQ": "267.71%"}, {"SOXL": "245.03%"}, {"TECL": "242.95%"}, 
            {"ROM": "218.33%"}, {"ARKG": "203.18%"}, {"QLD": "200.51%"}]
    
    etf_symbol = [list(pair.keys())[0] for pair in etf]
    names = get_etf_names_by_symbols(etf_symbol)
    
    for i in range(len(etf_symbol)):
        if names[i] != None:
            result["ETF"]["names"].append(names[i])
            percent = (float)(etf[i][list(etf[i].keys())[0]].split("%")[0])
            percent = percent / 300
            result["ETF"]["measures"].append(percent)
    return result

def get_growth_stocks(input):
    result={
        "stock": {
            "names" : [],
            "measures" : [],
            "history": {}
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
                    result["stock"]["history"][ticker] = get_history(ticker)
    return result
"""
    Only for stocks for now
"""
def get_history(name):
    history = []
    series = stocks[name]['history']

    if series is not None:
        for (index, price) in enumerate(series[::-1]):
            x = series.iloc[[index]]
            date = x.index.date[0].strftime("%m-%d-%Y")
            history.append([date, price])
    h = history[::-1]
    return h

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
            "history": {}
        },
    }
    # print(stocks)
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
                    ret['stock']['history'][ticker] = get_history(ticker)
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
            for i in range(len(measures)):
                if i == indexSmallestPeg:
                    measures[i] = 0.7
                else:
                    measures[i] = 0.15
        ret['stock']['names'] =  val_stock
        ret['stock']['measures'] = measures[:]
    # print(ret)
    return ret

def get_value_eft(input):
    ret={
        "ETF": {
            "names" : [],
            "measures" : [],
            "history": {}
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
        ret['ETF']['history'] = {'VTV':[[10, '1/02/2021'], [2, '1/02/2021'], [100, '1/02/2021'], [30, '1/02/2021'], [10, '1/02/2021']]}
    elif (useETF):
        ret['ETF']['names'] =  etf[:]
        ret['ETF']['measures'] = measures[:]
        ret['ETF']['history'] = {'VYM': [], 'VTV': [], 'SPY': []}
    # print(ret)
    return ret



def get_ethical_stocks(input):
    '''
    Choose 3 stocks from the top 10 companies that have made great efforts for the environment
    https://www.forbes.com/sites/justcapital/2019/04/22/the-top-33-companies-for-the-environment-by-industry/?sh=7bee72ce6461
    '''
    result={
        "stock": {
            "names" : [],
            "measures" : [],
        },
    }


    # result["stock"]["names"].append('MSFT')
    # print(stocks.keys())
    # print(stocks['date'])
    # for x, y in stocks.items():
    #     print("key")
    #     print(x)
    #     print("value")
    #     print(y)

    
    ethical_stock_tickers_top10 = ['MSFT', 'INTC', 'GOOGL', 'IBM', 'ACN', 'T', 'GM', 'GIS', 'AAPL', 'RMD']

    # recommendation score = 10 * past year percentage change + 5 * past 6-month percentage change + 3 * past 3-month percentage change
    recommendation_score_list = {}
    for ticker in ethical_stock_tickers_top10:
        tk = yf.Ticker(ticker)
        history = tk.history(period='1y')
        today_data = tk.history(period='1d')
        current_price = round(today_data['Close'][0], 2)
        total_rows = history.shape[0] 
        prev_year_price = history.iloc[0]['Close']
        prev_6month_price = history.iloc[round(total_rows * 0.5)]['Close']
        prev_3month_price = history.iloc[round(total_rows * 0.75)]['Close']         
        past_year_percetage_change = (current_price - prev_year_price) / prev_year_price
        past_6month_percentage_change = (current_price - prev_6month_price) / prev_6month_price 
        past_3month_percentage_change = (current_price - prev_3month_price) / prev_3month_price 
        recommendation_score = 10 * past_year_percetage_change +  5 * past_6month_percentage_change + 3 * past_3month_percentage_change 
        recommendation_score_list[ticker] = recommendation_score
    
    # sort recommendation score in descending order
    sorted_recommendation_score_list= sorted(recommendation_score_list.items(), key=lambda x: x[1], reverse=True)
    print("sorted list")
    print(sorted_recommendation_score_list)

    # output top 3 stock recommendations
    count = 0
    for stock_ticker, recommendation_score in sorted(recommendation_score_list.items(), key=lambda x: x[1], reverse=True):
        if count < 3:
            result["stock"]["names"].append(stock_ticker)
            count = count + 1 
    print("ethical stocks result:")
    print(result) 
    
    return result



def get_ethical_etfs(input):
    '''
    Choose 3 stocks from the top 10 ETFs that are environmentally responsible
    https://etfdb.com/esg-investing/environmental-issues/
    '''

    ret={
        "ETF": {
            "names" : [],
        },
    }

    
    ethical_etf_tickers_top10 = ['KGRN', 'ACES', 'ICLN', 'TAN', 'SMOG', 'CTEC', 'QCLN', 'RNRG', 'FAN', 'SDG']

    # recommendation score = 10 * past year percentage change + 5 * past 6-month percentage change + 3 * past 3-month percentage change
    recommendation_score_list = {}
    for ticker in ethical_etf_tickers_top10:
        tk = yf.Ticker(ticker)
        history = tk.history(period='1y')
        today_data = tk.history(period='1d')
        current_price = round(today_data['Close'][0], 2)
        total_rows = history.shape[0] 
        prev_year_price = history.iloc[0]['Close']
        prev_6month_price = history.iloc[round(total_rows * 0.5)]['Close']
        prev_3month_price = history.iloc[round(total_rows * 0.75)]['Close']         
        past_year_percetage_change = (current_price - prev_year_price) / prev_year_price
        past_6month_percentage_change = (current_price - prev_6month_price) / prev_6month_price 
        past_3month_percentage_change = (current_price - prev_3month_price) / prev_3month_price 
        recommendation_score = 10 * past_year_percetage_change +  5 * past_6month_percentage_change + 3 * past_3month_percentage_change 
        recommendation_score_list[ticker] = recommendation_score
    
    # sort recommendation score in descending order
    sorted_recommendation_score_list= sorted(recommendation_score_list.items(), key=lambda x: x[1], reverse=True)
    print("sorted list")
    print(sorted_recommendation_score_list)

    # output top 3 ETF recommendations
    count = 0
    for etf_ticker, recommendation_score in sorted(recommendation_score_list.items(), key=lambda x: x[1], reverse=True):
        if count < 3:
            ret["ETF"]["names"].append(etf_ticker)
            count = count + 1 
    print("ethical ETFs result:")
    print(ret) 
    
    return ret


def get_index_stocks(input):
    res = {
        "stock": {
            "names" : [],
            "measures" : [],
        },
    }
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
            if (s[1] == 0):
                measures.append(0.00001) 
            measures.append(s[1])  
    print (selected_tickers) 
    print (measures)      

    print (f'number of select tickers is {len(selected_tickers)}')
    if (useStock and useETF) :
        selected_tickers.pop()
        measures.pop()
        res["stock"]["names"] = selected_tickers
        res["stock"]["measures"] =  measures
    elif (useStock):
        res["stock"]["names"] = selected_tickers
        res["stock"]["measures"] =  measures
    print (res)
    return res

def get_index_etfs(input):
    res={
        "ETF": {
            "names" : [],
            "measures" : [],
        },
    }
    '''
    source: https://www.bankrate.com/investing/best-index-funds/
    VOO: expense ratio = 0.03%
    SPY: expense ratio = 0.09%
    IVV: expense ratio = 0.03%
    '''
    etf = ['VOO', 'SPY', 'IVV']
    measures = [0.0003, 0.0009, 0.0003]
    products = input['products'].split(',')
    useStock = 'stock' in products
    useETF = 'etf' in products
    if (useStock and useETF) :
        res["ETF"]["names"] = etf[2:]
        res["ETF"]["measures"] =  measures[2:]
    elif (useETF):
        res["ETF"]["names"] = etf
        res["ETF"]["measures"] = measures
    print (res)
    return res    

handlerMap = {
    "stock":{
        "ethical": get_ethical_stocks,
        "growth": get_growth_stocks,
        "quality": None,
        "index": get_index_stocks,
        "value": get_value_stocks,
    },
    "etf": {
        "ethical": get_ethical_etfs,
        "growth": get_growth_etfs,
        "quality": None,
        "index": get_index_etfs,
        "value": get_value_eft,
    },
}

