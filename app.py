from flask import Flask, render_template, request
from functions import getSuggestions
from stockService import update
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(1)
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('main.html')


@app.route('/', methods=['POST']) 
def query():

    suggestion = getSuggestions(request.form)
    
    viewItems = {}
    strats = request.form['strats'].split(",")
    strat1 = strats[0]
    viewItems['amount'] = request.form['amount']
    viewItems['strat1'] = strat1
    if (len(strats) == 2):
        viewItems['strat2'] = strats[1]
    viewItems['suggestion'] = suggestion
    return render_template('main.html', items=viewItems)

if __name__ == '__main__':
    executor.submit(update)
    app.run(debug=True)
    
    