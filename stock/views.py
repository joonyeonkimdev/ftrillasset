from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.
def backtest(request):
    if request.method != "POST":
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