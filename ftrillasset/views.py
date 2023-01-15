from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
import pymysql
import utils.loading.confidential as confidential
from datetime import datetime
from utils.stockdb.DBUpdater import DBUpdater

def home(request):
   conn = pymysql.connect\
            (host="localhost", port=3306, db="FTRILL", user="root", password=confidential.get_confidential('databasepw.json', "PASSWORD"), charset="utf8")
   with conn.cursor() as cursor:
      sql = "SELECT MAX(LAST_UPDATE) FROM COMPANY_INFO_TB"
      cursor.execute(sql)
      rs = cursor.fetchone()
      today = datetime.today().strftime("%Y-%m-%d")
      if rs[0] == None or rs[0].strftime("%Y-%m-%d") < today:
         conn.close()
         return redirect(reverse('wait'))
   conn.close()
   return render(request, 'ftrillasset/home.html')

def wait(request):
   context = {'msg':'서버 최신화 중입니다. 잠시만 기다려 주십시오.', 'url':'dbupdate'}
   return render(request, 'wait.html', context)

def dbupdate(request):
   dbupdater = DBUpdater()
   dbupdater.execute_daily()
   del dbupdater
   print("The DB connection terminated")
   return redirect(reverse('home'))