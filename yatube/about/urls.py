from . import views
from django.urls import path


app_name = 'about'

urlpatterns = [
    path('author/', views.AboutAuthor.as_view(), name='author'),
    path('tech/', views.AboutTech.as_view(), name='tech'),
]
