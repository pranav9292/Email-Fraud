from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_email, name='upload_email'),  # Default route
    path('upload/', views.upload_email, name='upload_email'),
]
