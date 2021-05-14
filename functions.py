import requests
import pandas as pd
import yfinance as yf
import time

def getSuggestions(input):
    strats = input["strats"].split(",")
    products = input["products"].split(",")
    for product in products:
        for strat in strats:
            handler = handlerMap[product][strat]
            if handler != None:
                handler()
    
    result={
        "stock": {
            "spend" : (int)(input["amount"])/3,
            "names" : ["Google", "Apple"],
        }, 
        "ETF": {
            "spend" : (int)(input["amount"])/3 * 2,
            "names" : ["iShares U.S. Medical Devices ETF"]
        }}
    return result

# Large cap stocks
def get_sp500_tickers():
    wiki_table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = wiki_table[0]
    tickers = df['Symbol'].values
    # print(tickers)
    return tickers

# Medium cap stocks
def get_sp400_tickers():
    wiki_table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_400_companies')
    df = wiki_table[0]
    # print(df)
    tickers = df['Ticker symbol'].values
    # print(tickers)
    return tickers

# Small cap stocks
def get_sp600_tickers():
    wiki_table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_600_companies')
    df = wiki_table[1]
    # print(df)
    tickers = df['Ticker symbol'].values
    # print(tickers)
    return tickers

def grab_all_stocks():
    ret = {}
    ret["small"] = get_sp600_tickers()
    ret["medium"] = get_sp400_tickers()
    ret["large"] = get_sp500_tickers()
    return ret

def value_selection(amount, stocks):
    # from the list of stocks, return top three and amount to each stocks
    # select from large cap stocks and choose one that suffered drop recently or traded sideways for a while
    sp500 = get_sp500_tickers()

    return

stocks = grab_all_stocks()    

def get_growth_stocks():
    small = stocks['small']
    tickerList = ""
    for i in range(1):
        test = "AMZN"
        stock = yf.Ticker(test)
        print(stock.earnings)
    return None

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

