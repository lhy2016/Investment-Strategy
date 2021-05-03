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