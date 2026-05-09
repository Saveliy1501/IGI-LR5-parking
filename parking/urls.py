from django.contrib import admin
from django.urls import path, include   
from parking_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('parking_app.urls')),   
]