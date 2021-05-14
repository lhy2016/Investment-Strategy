from functions import grab_all_stocks
import time
import datetime as dt
from pytz import timezone
import os

stocks = grab_all_stocks()
file = None
while True:
    
    ue = timezone('US/Eastern')
    hh = dt.datetime.now(ue).hour 
    if hh >= 20 or os.stat('stocksInfo.txt').st_size == 0:
        yy = dt.datetime.now(ue).year
        mm = dt.datetime.now(ue).month
        dd = dt.datetime.now(ue).day
        todayStr = str(yy) + "-" + str(mm) + "-" + str(dd)
        
        file = open('stocksInfo.txt', 'w+')
        dateStr = file.readline()
        if not dateStr or dateStr != todayStr:
            file.write(todayStr)
            for cap in stocks:
                stockList = stocks[cap]
                for ticker in stockList:
                    file.write("\n"+ticker)
        file.close()
    time.sleep(6)