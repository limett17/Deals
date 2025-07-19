from django.urls import path

from contacts.views.contacts import contacts
from contacts.views.export_contacts import export_contacts
from contacts.views.import_contacts import import_contacts


urlpatterns = [
    path('', contacts, name='contacts'),
    path('import/', import_contacts, name='import_contacts'),
    path('export/', export_contacts, name='export_contacts'),
]