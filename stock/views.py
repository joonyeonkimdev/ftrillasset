from django.shortcuts import render
from django.http import HttpResponseRedirect
import utils.tmethod.bollingerband as bb
import utils.tmethod.triplescreen as ts
import utils.tmethod.dualmomentum as dm
import utils.tmethod.candlestic as candle

# Create your views here.
def backtest(request, company=None, start_date=None, end_date=None):
    if request.method != "POST":
        candle_chart_filename = candle.candlestic(company, start_date, end_date)
        return render(request, 'stock/backtest.html')
    else:
        pass

def simulate(request):
    if request.method != "POST":
        return render(request, 'stock/simulate.html')
    else:
        pass

def portfolio(request):
    if request.method != "POST":
        return render(request, 'stock/portfolio.html')
    else:
        pass