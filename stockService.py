import time
import datetime as dt
from pytz import timezone
import yfinance as yf
import pandas as pd

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

stocks = {}
delisted = ["BRK.B", "MOG.A", "JW.A", "TPRE", "BF.B"]

def update():
    while True:    
        ue = timezone('US/Eastern')
        hh = dt.datetime.now(ue).hour 
        if hh >= 20 or "date" not in stocks:
            yy = dt.datetime.now(ue).year
            mm = dt.datetime.now(ue).month
            dd = dt.datetime.now(ue).day
            todayStr = str(yy) + "-" + str(mm) + "-" + str(dd)
            if "date" not in stocks: 
                stocks["date"] = todayStr
                tickers = grab_all_stocks()
                tickers = [*tickers["small"], *tickers["medium"], *tickers["large"]]
                tickers = list(set(tickers))
                tickers = [x for x in tickers if x not in delisted]
                tickerStr = " ".join(tickers)

                data = yf.download(tickerStr, period="1y", interval="1wk",threads=True, group_by='tickers')
                for ticker in tickers:
                    stocks[ticker] = {}
                    updated = data.loc[:, (ticker, "High")].dropna()
                    if(len(updated) > 0):
                        stocks[ticker]["history"] = updated
                        tickerObj = yf.Ticker(ticker)
                        stocks[ticker]["quarterly_earnings"] = tickerObj.quarterly_earnings
                        stocks[ticker]["info"] = tickerObj.info
                        stocks[ticker]["earnings"] = tickerObj.earnings
                print("initialization finished!")

            elif stocks["date"] != todayStr:
                stocks["date"] = todayStr
                for ticker in stocks.keys():
                    if ticker != "date":
                        tickerObj = yf.Ticker(ticker)
                        updated = tickerObj.history(period="1y", interval="1wk")
                        if (len(updated) > 0):
                            stocks[ticker]["history"] = updated
                            stocks[ticker]["quarterly_earnings"] = tickerObj.quarterly_earnings
                            stocks[ticker]["info"] = tickerObj.info
                            stocks[ticker]["earnings"] = tickerObj.earnings
                        else:
                            del stocks[ticker]
        time.sleep(3600)