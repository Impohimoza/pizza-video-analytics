from django.urls import path
from . import views

urlpatterns = [
    path('pizzas/', views.pizza_list, name='pizza_list'),
    path('pizzas/<int:pizza_id>/', views.pizza_detail, name='pizza_detail'),
    path('pizzas/<int:pizza_id>/delete/', views.delete_pizza, name='delete_pizza'),
    path('pizzas/add/', views.add_pizza, name='add_pizza'),
    # другие маршруты позже
]
