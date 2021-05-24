from investpy.etfs import get_etf_historical_data
from numpy.testing._private.utils import measure
import random
import pandas as pd
import yfinance as yf
from stockService import stocks, update
import investpy as ipy
from datetime import datetime
import datetime as dt
import json


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
                    curProduct = list(temp.keys())[0]
                    curTickers = result[curProduct]["names"]
                    toAddTickers = temp[curProduct]["names"]
                    
                    curFullNames = result[curProduct]["full_names"] if curProduct == "stock" else None
                    toAddFullNames = temp[curProduct]["full_names"] if curProduct == "stock" else None

                    curMeasures = result[curProduct]["measures"]
                    toAddMeasures = temp[curProduct]["measures"]

                    curHistory = result[curProduct]["history"]
                    toAddHistory = temp[curProduct]["history"]
                    for i in range(len(toAddTickers)):
                        ticker = toAddTickers[i]
                        if ticker in curTickers:
                            index = curTickers.index(ticker)
                            curMeasures[index] = curMeasures[index] + toAddMeasures[i]
                        else:
                            curTickers.append(ticker)
                            if curProduct == "stock":
                                curFullNames.append(toAddFullNames[i])
                            curMeasures.append(toAddMeasures[i])
                            curHistory[ticker] = toAddHistory[ticker]

    allsum = 0
    for key in result:
        productRateAve = 0
        productRateSum = sum(result[key]["measures"])
        productRateAve = 0 if len(result[key]["measures"]) == 0 else productRateSum / len(result[key]["measures"])
        result[key]["rate_ave"] = productRateAve
        result[key]["rate_sum"] = productRateSum
        result[key]["ratio"] = [(0 if productRateSum == 0 else tickerRate/productRateSum) for tickerRate in result[key]["measures"]]
        allsum += productRateAve
    for key in result:
        result[key]["spend"] = 0 if allsum == 0 else round((int)(input["amount"]) * (result[key]["rate_ave"] / allsum) , 2)
        if key == "stock":
            result[key]["current"] = []
            for name in result[key]["names"]:
                ticker = yf.Ticker(name)
                history = ticker.history(period="1d", interval="1m")
                lastMin = history.iloc[-1]['Close']
                result[key]["current"].append(lastMin)
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
            "history" : {},
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
            percent = percent / 100
            percent = pow(percent, 1/3)
            result["ETF"]["measures"].append(percent)
            result["ETF"]["history"][names[i]] = get_eft_history(names[i])
    return result

def get_growth_stocks(input):
    result={
        "stock": {
            "names" : [],
            "full_names" : [],
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
                    result["stock"]["full_names"].append("" if "shortName" not in stocks[ticker]["info"] else stocks[ticker]["info"]["shortName"])
                    result["stock"]["measures"].append(rateSum/years)
                    result["stock"]["history"][ticker] = get_history(ticker)

                    if len(result["stock"]["names"]) == 10:
                        break
    return result
"""
    Only for stocks for now
"""
def get_history(name):
    history = []
    series = stocks[name]['history']
    if series is not None:
        for i in range(min(len(series), 7)):
            x = series.iloc[[-(i+1)]]
            date = x.index.date[0].strftime("%m-%d-%Y")
            price = x.values[0]
            history.append([date, price])
    return history[::-1]
"""
    Pass in etf name
    returns array formatted for chart.js
"""
def get_eft_history(name):
    history = []
    date = datetime.now().date()
    curr_date = "{}/{}/{}".format("{0:0=2d}".format(date.day), "{0:0=2d}".format(date.month), "{0:0=2d}".format(date.year))
    weekAgo = datetime.now() - dt.timedelta(days=7)
    week_ago = "{}/{}/{}".format("{0:0=2d}".format(weekAgo.day), "{0:0=2d}".format(weekAgo.month), "{0:0=2d}".format(weekAgo.year))

    jsonStr = ipy.etfs.get_etf_historical_data(etf=name,
                                        country='United States',
                                        from_date=week_ago,
                                        to_date=curr_date, as_json=True)
    if jsonStr:
        jsonObj = json.loads(jsonStr)
        for obj in jsonObj["historical"]:
            dateStr = obj["date"]
            dateArr = dateStr.split("/")
            mon = dateArr[1]
            day = dateArr[0]
            yr = dateArr[2]
            date = mon + "-" + day + "-" + yr
            pr = obj["high"]
            history.append([date, pr])
    return history

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
            "full_names": [],
            "measures" : [],
            "history": {}
        },
    }
    #print(stocks)
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
            if "marketCap" not in info:
                ticker = random.choice(list(stocks.keys()))
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
        ret["stock"]["full_names"] = [ ("" if "shortName" not in stocks[n]["info"] else stocks[n]["info"]["shortName"]) for n in val_stock]
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
        ret["stock"]["full_names"] = [ ("" if "shortName" not in stocks[n]["info"] else stocks[n]["info"]["shortName"]) for n in val_stock]
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
    full_etf = get_etf_names_by_symbols(etf)
    vtv = get_etf_names_by_symbols(['VTV'])

    measures = [0.25, 0.5, 0.25]
    products = input['products'].split(',')
    useStock = 'stock' in products
    useETF = 'etf' in products
    if (useStock and useETF) :
        ret['ETF']['names'] = ['VTV'][:]
        ret['ETF']['measures'] = [0.25]
        final_hist = {}
        for i in vtv:
            tmp_hist = get_eft_history(i)
            final_hist['VTV'] = tmp_hist
        # print(final_hist)
        ret['ETF']['history'] = final_hist
    elif (useETF):
        ret['ETF']['names'] =  etf[:]
        ret['ETF']['measures'] = measures[:]
        final_hist = {}
        for index, i in enumerate(full_etf):
            tmp_hist = get_eft_history(i)
            final_hist[etf[index]] = tmp_hist
        # print(final_hist)
        ret['ETF']['history'] = final_hist
    return ret



def get_ethical_stocks(input):
    '''
    Choose 3 stocks from the top 10 companies that have made great efforts for the environment
    https://www.forbes.com/sites/justcapital/2019/04/22/the-top-33-companies-for-the-environment-by-industry/?sh=7bee72ce6461
    '''
    result={
        "stock": {
            "names" : [],
            "full_names": [],
            "measures" : [],
            "history": {},
        },
    }
    
    ethical_stock_tickers_top10 = ['MSFT', 'INTC', 'GOOGL', 'IBM', 'ACN', 'T', 'GM', 'GIS', 'AAPL', 'RMD']

    # recommendation score = 10 * past year percentage change + 5 * past 6-month percentage change + 3 * past 3-month percentage change
    recommendation_score_list = {}
    for ticker in ethical_stock_tickers_top10:
        if ticker not in stocks:
            continue
        tk = stocks[ticker]
        history = tk["history"]
        today_data = history.iloc[-1:]
        current_price = round(today_data.values[0], 2)
        total_rows = len(history)
        prev_year_price = round(history.iloc[0], 2)
        prev_6month_price = round(history.iloc[round(total_rows * 0.5)], 2)
        prev_3month_price = round(history.iloc[round(total_rows * 0.75)], 2)         
        past_year_percetage_change = (current_price - prev_year_price) / prev_year_price
        past_6month_percentage_change = (current_price - prev_6month_price) / prev_6month_price 
        past_3month_percentage_change = (current_price - prev_3month_price) / prev_3month_price 
        recommendation_score = 10 * past_year_percetage_change +  5 * past_6month_percentage_change + 3 * past_3month_percentage_change 
        recommendation_score_list[ticker] = recommendation_score
    
    # sort recommendation score in descending order
    sorted_recommendation_score_list= sorted(recommendation_score_list.items(), key=lambda x: x[1], reverse=True)
  

    # output top 3 stock recommendations
    count = 0
    for stock_ticker, recommendation_score in sorted_recommendation_score_list:
        if count < 3:
            result["stock"]["names"].append(stock_ticker)
            result["stock"]["full_names"].append("" if "shortName" not in stocks[stock_ticker]["info"] else stocks[stock_ticker]["info"]["shortName"])
            result["stock"]["measures"].append(recommendation_score)
            result["stock"]["history"][stock_ticker] = get_history(stock_ticker)
            count = count + 1 
        else: 
            break
    return result



def get_ethical_etfs(input):
    '''
    Choose 3 stocks from the top 10 ETFs that are environmentally responsible
    https://etfdb.com/esg-investing/environmental-issues/
    '''

    ret={
        "ETF": {
            "names" : [],
            "measures": [],
            "history": {},
        },
    }

    
    ethical_etf_tickers_top10 = ['KGRN', 'ACES', 'ICLN', 'TAN', 'SMOG', 'CTEC', 'QCLN', 'RNRG', 'FAN', 'SDG']

    # recommendation score = 10 * past year percentage change + 5 * past 6-month percentage change + 3 * past 3-month percentage change
    recommendation_score_list = {}
    for ticker in ethical_etf_tickers_top10:
        if ticker not in stocks:
            continue
        tk = stocks[ticker]
        history = tk["history"]
        today_data = history.iloc[-1:]
        current_price = round(today_data.values[0], 2)
        total_rows = len(history)
        prev_year_price = round(history.iloc[0], 2)
        prev_6month_price = round(history.iloc[round(total_rows * 0.5)], 2)
        prev_3month_price = round(history.iloc[round(total_rows * 0.75)], 2)         
        past_year_percetage_change = (current_price - prev_year_price) / prev_year_price
        past_6month_percentage_change = (current_price - prev_6month_price) / prev_6month_price 
        past_3month_percentage_change = (current_price - prev_3month_price) / prev_3month_price 
        recommendation_score = 10 * past_year_percetage_change +  5 * past_6month_percentage_change + 3 * past_3month_percentage_change 
        recommendation_score_list[ticker] = recommendation_score
    
    # sort recommendation score in descending order
    sorted_recommendation_score_list= sorted(recommendation_score_list.items(), key=lambda x: x[1], reverse=True)
    

    # output top 3 ETF recommendations
    count = 0
    for etf_ticker, recommendation_score in sorted_recommendation_score_list:
        if count < 3:
            ret["ETF"]["names"].append(etf_ticker)
            ret["ETF"]["measures"].append(recommendation_score)
            ret["ETF"]["history"][etf_ticker] = get_history(etf_ticker)
            count = count + 1 
    return ret


def get_index_stocks(input):
    res = {
        "stock": {
            "names" : [],
            "full_names": [],
            "measures" : [],
            "history": {}
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
            if info['annualReportExpenseRatio'] <= 0.01:
                stock_dic[ticker] = info['annualReportExpenseRatio']
            
    sort_stocks = sorted(stock_dic.items(), key=lambda x: x[1])
    for s in sort_stocks:
        if len(selected_tickers) <=2:
            selected_tickers.append(s[0])
            if (s[1] == 0):
                measures.append(0.00001) 
            measures.append(s[1])  
    if (useStock and useETF) :
        selected_tickers.pop()
        measures.pop()
        res["stock"]["names"] = selected_tickers
        res["stock"]["measures"] =  measures
    elif (useStock):
        res["stock"]["names"] = selected_tickers
        res["stock"]["measures"] =  measures
    return res

def get_index_etfs(input):
    res={
        "ETF": {
            "names" : [],
            "measures" : [],
            "history" : {},
        },
    }
    '''
    source: https://www.bankrate.com/investing/best-index-funds/
    VOO: expense ratio = 0.03%
    SPY: expense ratio = 0.09%
    IVV: expense ratio = 0.03%
    '''
    etf = ['VOO', 'SPY', 'IVV']
    names = get_etf_names_by_symbols(etf)
    measures = [0.4, 0.2, 0.4]

    for i in range(len(etf)):
        if names[i] != None:
            res["ETF"]["names"].append(etf[i])
            res["ETF"]["measures"].append(measures[i])
            res["ETF"]["history"][etf[i]] = get_eft_history(names[i])
    return res    

def get_quality_stocks(input):
    res={
        "stock": {
            "names" : [],
            "full_names": [],
            "measures" : [],
            "history" : {},
        },
    }

    #https://www.risk.net/definition/quality-factor#:~:text=The%20quality%20factor%20refers%20to,over%20a%20long%20time%20horizon.&text=Quality%2Dbased%20strategies%20try%20to,stocks%20versus%20low%2Dquality%20stocks.
    # use payoutRatio as metric, the higher the better
    selected_stocks = {}
    for ticker in [key for key in stocks.keys() if key != "date"]:

        stock = stocks[ticker]
        if 'info' in stock:
            info = stock['info']
            if 'payoutRatio' in info:
                payoutRatio = info['payoutRatio']
                if  payoutRatio is not None and payoutRatio >= 0.35:
                    selected_stocks[ticker] = payoutRatio
            if len(selected_stocks) > 2:
                break
    sort_stocks = sorted(selected_stocks.items(), key=lambda x: x[1], reverse=True)
    for s in sort_stocks:
        res["stock"]["names"].append(s[0])
        res["stock"]["full_names"].append("" if "shortName" not in stocks[s[0]]["info"] else stocks[s[0]]["info"]["shortName"])
        res["stock"]["measures"].append(s[1])
        res["stock"]["history"][s[0]] = get_history(s[0])
    return res

def get_quality_etfs(input):
    res={
        "ETF": {
            "names" : [],
            "measures" : [],
            "history" : {},
        },
    }
    #https://www.etf.com/sections/features-and-news/dissecting-3-big-quality-etfs
    #https://www.nasdaq.com/articles/5-solid-quality-etfs-to-buy-now-2021-03-26
    selected_etfs = []
    etf = {"QUAL": 0.1658, "SPHQ": 0.1565, "DGRW": 0.1659, "QDF": 0.1291, "IQLT": 0.1197, "IQDF": 0.088599995, "BFOR":0.1524, "QDF":0.1291, "QUS": 0.16420001}
    sort_etfs = sorted(etf.items(), key=lambda x: x[1], reverse=True)
    measures = [0.5, 0.3, 0.2]
    for e in sort_etfs:
        if len(selected_etfs) <=2:
            selected_etfs.append(e[0])
            measures.append(measures[len(selected_etfs) - 1])  

    names = get_etf_names_by_symbols(selected_etfs)

    for i in range(len(selected_etfs)):
        if names[i] != None:
            res["ETF"]["names"].append(selected_etfs[i])
            res["ETF"]["measures"].append(measures[i])
            res["ETF"]["history"][selected_etfs[i]] = get_eft_history(names[i])
    return res

handlerMap = {
    "stock":{
        "ethical": get_ethical_stocks,
        "growth": get_growth_stocks,
        "quality": get_quality_stocks,
        "index": get_index_etfs,
        "value": get_value_stocks,
    },
    "etf": {
        "ethical": get_ethical_etfs,
        "growth": get_growth_etfs,
        "quality": get_quality_etfs,
        "index": get_index_etfs,
        "value": get_value_eft,
    },
}

