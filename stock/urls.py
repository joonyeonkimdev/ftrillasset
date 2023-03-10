from django.urls import path
from . import views

urlpatterns = [
    path('backtest', views.backtest, name='backtest'),
    path('backtest/<str:company>/<slug:start_date>/<slug:end_date>', views.backtest, name='backtest'),
    path('simulate', views.simulate, name='simulate'),
    path('simulate/<str:company>/<slug:start_date>/<slug:end_date>', views.simulate, name='simulate'),
    path('wait', views.wait, name='wait'),
    path('predict', views.predict, name='predict'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('bollingerband', views.bollingerband, name='bollingerband'),
    path('triplescreen', views.triplescreen, name='triplescreen'),
    path('dualmomentum', views.dualmomentum, name='dualmomentum'),
]