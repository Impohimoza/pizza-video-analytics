from django.urls import path
from . import views

urlpatterns = [
    path('', views.evaluation_list, name='evaluation_list'),
    path('export/', views.evaluation_export, name='evaluation_export'),
    path('<int:evaluation_id>/', views.evaluation_detail, name='evaluation_detail'),
    path('api/create_evaluation/', views.create_evaluation_api, name='create_evaluation_api'),
]
