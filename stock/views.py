from django.shortcuts import render
from django.http import HttpResponseRedirect
import utils.tmethod.bollingerband as bb
import utils.tmethod.triplescreen as ts
import utils.tmethod.dualmomentum as dm
import utils.tmethod.candlestic as candle

# Create your views here.
def backtest(request):
    if request.method != "POST":
        company = request.GET.get('company')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if company != None:
            filename = candle.candlestic(company, start_date, end_date)
            print(filename+"+++++++++++++++++++++++++++++++++++++++++++++++++++")
            return render(request, 'stock/backtest.html', {'filename':filename})
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