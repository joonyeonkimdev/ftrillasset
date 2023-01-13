from django.urls import path
from . import views

urlpatterns = [
    path('backtest', views.backtest, name='backtest'),
    path('backtest/<str:company>/<slug:start_date>/<slug:end_date>', views.backtest, name='backtest'),
    path('simulate', views.simulate, name='simulate'),
    path('portfolio', views.portfolio, name='portfolio'),
]