from django.urls import path
from . import views

urlpatterns = [
    path('', views.compress_and_qr, name='compress_and_qr'),
]
