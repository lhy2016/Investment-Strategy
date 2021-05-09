import requests
import pandas as pd

# Medium cap stocks
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
    print(df)
    tickers = df['Ticker symbol'].values
    # print(tickers)
    return tickers

def getSuggestions(amount, strats):
    result={
        "stock": {
            "spend" : amount/3,
            "names" : ["Google", "Apple"],
        }, 
        "ETF": {
            "spend" : amount/3 * 2,
            "names" : ["iShares U.S. Medical Devices ETF"]
        }}
    return result

def value_selection(amount, stocks):
    # from the list of stocks, return top three and amount to each stocks
    # select from large cap stocks and choose one that suffered drop recently or traded sideways for a while
    sp500 = get_sp500_tickers()

    return
    
def grab_all_stocks():
    api_key = '97PWgrqMl_bpqgzX9KGLEJvIaN3pq7yJ'

    response1 = requests.get('https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&sort=ticker&order=asc&limit=1000&apiKey=' + api_key)
    ret = []
    while 1:
        data = response1.json()
        for stock in data['results']:
            ret.append(stock['ticker'])

        if (data.__contains__('next_url')):
            url = data['next_url']
            response1 = requests.get(url + '&apiKey=' + api_key)
        else:
            # print(data['results'][-1])
            break
        break
    print("Total # of stocks: " + str(len(ret)))
    return ret