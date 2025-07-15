from django.urls import path
from people.views.list_people import list_people
# from people.views.generate_calls import generate_calls

urlpatterns = [
    path('list/', list_people, name='list_people'),
    # path('generate_calls/', generate_calls, name='generate_calls'),
]
