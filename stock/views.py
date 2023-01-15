from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from pathlib import Path
import os
import utils.tmethod.bollingerband as bb
import utils.tmethod.triplescreen as ts
import utils.tmethod.dualmomentum as dm
import utils.tmethod.candlestic as candle
import utils.falearn.falearn as falearn
import json
from django.http import JsonResponse

BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.


def backtest(request):
    if request.method != "POST":
        company = request.GET.get('company', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        if company != None:
            remove_all_files()
            filename = candle.candlestic(company, start_date, end_date)
            context = {'filename': filename, "company": company,
                       "start_date": start_date, "end_date": end_date}
            return render(request, 'stock/backtest.html', context)
        return render(request, 'stock/backtest.html')
    else:
        pass


def simulate(request):
    if request.method != "POST":
        company = request.GET.get('company', "")
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        context = {"company": company, "start_date": start_date, "end_date": end_date}
        return render(request, 'stock/simulate.html', context)
    else:
        pass

def wait(request):
    company = request.GET.get('company', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
#    context = {'msg': 'AI 예측 데이터를 생성 중입니다. 잠시만 기다려 주십시오.',
#               'url': f"predict?company={company}&start_date={start_date}&end_date={end_date}"}
    context = {'msg': 'AI 예측 데이터를 생성 중입니다. 잠시만 기다려 주십시오.',
                "company": company, "start_date": start_date, "end_date": end_date}
    return render(request, 'stock/wait.html', context)

def predict(request):
    company = request.GET.get('company', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    if company != None:
        last_date = falearn.predict(company)
        end_date = last_date
        remove_all_files()
        filename = candle.candlestic(company, start_date, end_date)
        context = {'filename': filename, "company": company, "start_date": start_date, "end_date": end_date}
        return render(request, 'stock/simulate.html', context)
    return redirect(reverse('simulate'))

def portfolio(request):
    if request.method != "POST":
        return render(request, 'stock/portfolio.html')
    else:
        pass

def bollingerband(request):
    json_obj = json.loads(request.body)
    company = json_obj.get('company')
    start_date = json_obj.get('start_date')
    end_date = json_obj.get('end_date')
    bollingerband = json_obj.get('bollingerband')

    remove_all_files()
    filename1 = bb.bollingerband1(company, start_date, end_date)
    filename2 = bb.bollingerband2(company, start_date, end_date)
    rr = bb.earingrate(company, start_date, end_date)
    data = {'filename1': filename1, 'filename2': filename2, 'rr': rr}
    return JsonResponse(data)


def triplescreen(request):
    json_obj = json.loads(request.body)
    company = json_obj.get('company')
    start_date = json_obj.get('start_date')
    end_date = json_obj.get('end_date')
    triplescreen = json_obj.get('triplescreen')

    remove_all_files()
    filename = ts.tsgraph(company, start_date, end_date)
    rr = ts.tsrevenue(company, start_date, end_date)
    data = {'filename': filename, 'rr': rr}
    return JsonResponse(data)


def dualmomentum(request):
    json_obj = json.loads(request.body)
    company = json_obj.get('company')
    start_date = json_obj.get('start_date')
    end_date = json_obj.get('end_date')
    dualmomentum = json_obj.get('dualmomentum')

    remove_all_files()
    dualmomentum_list = dm.mmt()

    if company in dualmomentum_list:
        dualmomentum_flag = '모멘텀 종목입니다.<br>해당 종목은 상승장에 있습니다.'
    else:
        dualmomentum_flag = '모멘텀 종목이 아닙니다.<br>해당 종목은 하락장 또는 횡보장에 있습니다.'

    data = {'dualmomentum_flag': dualmomentum_flag}
    return JsonResponse(data)


def remove_all_files():
    stock_img_dir = str(BASE_DIR) + '/static/stock_img'
    if os.path.exists(stock_img_dir):
        for file in os.scandir(stock_img_dir):
            os.remove(file.path)
