from django.urls import path
from . import views

urlpatterns = [
    path('', views.pizza_list, name='pizza_list'),
    path('<int:pizza_id>/', views.pizza_detail, name='pizza_detail'),
    path('<int:pizza_id>/delete/', views.delete_pizza, name='delete_pizza'),
    path('requests/', views.pizza_requests_view, name='requests_pizza'),
    path('from-request/<int:request_id>/', views.add_pizza_from_request, name='add_pizza_from_request'),
    path('api/create_requests/', views.create_pizza_request, name='create_pizza_request'),
    # другие маршруты позже
]
