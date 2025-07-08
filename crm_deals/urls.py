from django.urls import path

from .views.create_deal import create_deal
from .views.show_recent_deals import show_recent_deals
from .views.reload import reload_start

urlpatterns = [
    path('', reload_start, name='reload_start'),
    path('show_deals/', show_recent_deals),
    path('create_deal/', create_deal),
]
