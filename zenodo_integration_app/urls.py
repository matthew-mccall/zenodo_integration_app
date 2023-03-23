
from django.urls import path

from . import views

app_name = 'zenodo_integration_app'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('zenodo_callback/', views.zenodo_callback, name='zenodo_callback'),
    path('zenodo_upload/', views.zenodo_upload, name='zenodo_upload'),
    path('zenodo_upload_file/', views.zenodo_upload_file, name='zenodo_upload_file'),
]
