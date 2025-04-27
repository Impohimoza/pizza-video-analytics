from django.urls import path
from . import views

urlpatterns = [
    path('', views.evaluation_list, name='evaluation_list'),
    path('export/', views.evaluation_export, name='evaluation_export'),
    path('<int:evaluation_id>/', views.evaluation_detail, name='evaluation_detail'),
    path('api/create_evaluation/', views.create_evaluation_api, name='create_evaluation_api'),
    path('stream/<int:location_id>/', views.stream_camera, name='stream_camera'),
    path('cameras/', views.camera_page, name='camera_page'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/open/', views.notification_redirect, name='notification_redirect'),
    path('notifications/check/', views.check_new_notifications, name='check_notifications'),
    path('reports/', views.reports_page, name='reports_page'),
]
