import requests

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