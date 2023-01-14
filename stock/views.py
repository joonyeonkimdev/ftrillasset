from django.shortcuts import render
from django.http import HttpResponseRedirect
from pathlib import Path
import os
import utils.tmethod.bollingerband as bb
import utils.tmethod.triplescreen as ts
import utils.tmethod.dualmomentum as dm
import utils.tmethod.candlestic as candle
import json

BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.
def backtest(request):
    if request.method != "POST":
        company = request.GET.get('company', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        if company != None:
            stock_img_dir = str(BASE_DIR) + '/static/stock_img'
            if os.path.exists(stock_img_dir):
                for file in os.scandir(stock_img_dir):
                    os.remove(file.path)
            filename = candle.candlestic(company, start_date, end_date)
            context = {'filename':filename, "company":company, "start_date":start_date, "end_date":end_date}
            return render(request, 'stock/backtest.html', context)
        return render(request, 'stock/backtest.html')
    else:
        pass

def bollingerband(request):
    json_Obj = json.loads(request.body)
    company = json_Obj.get('company')
    start_date = json_Obj.get('start_date')
    end_date = json_Obj.get('end_date')
    bollingerband = json_Obj.get('bollingerband')

    filename1 = bb.bollingerband1(company, start_date, end_date)
    

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